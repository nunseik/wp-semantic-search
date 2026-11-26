"""Retrieval eval: does the search find the right articles for real questions?

Builds a fresh index from a fixed snapshot (eval/articles.jsonl) and runs every
question in eval/questions.jsonl, scoring the top-k articles against the expected ones.

    python eval/run_eval.py                                      # default model
    python eval/run_eval.py --model intfloat/multilingual-e5-base
    python eval/run_eval.py --min-recall 0.6                     # exit 1 below this (CI)

Metrics (averaged over questions):
  recall@k  share of a question's expected articles found in the top k
  hit@k     share of questions with at least one expected article in the top k
  MRR       mean of 1/rank of the first expected article (0 if none in the top k)
"""
import argparse
import json
import os
import shutil
import sys
import tempfile
import time

EVAL_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(EVAL_DIR)


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def score(expected, ranked_ids):
    expected = set(expected)
    found = [i for i in ranked_ids if i in expected]
    first = next((rank for rank, i in enumerate(ranked_ids, 1) if i in expected), None)
    return {
        "recall": len(found) / len(expected),
        "hit": 1.0 if found else 0.0,
        "rr": 1.0 / first if first else 0.0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--model", help="embedding model (default: config.MODEL_NAME)")
    parser.add_argument("--k", type=int, default=5, help="articles retrieved per question (default 5)")
    parser.add_argument("--questions", default=os.path.join(EVAL_DIR, "questions.jsonl"))
    parser.add_argument("--articles", default=os.path.join(EVAL_DIR, "articles.jsonl"))
    parser.add_argument("--min-recall", type=float, help="exit with status 1 if recall@k is below this")
    parser.add_argument("--summary", help="append a Markdown report to this file (e.g. $GITHUB_STEP_SUMMARY)")
    parser.add_argument("--quiet", action="store_true", help="only print misses and the totals")
    args = parser.parse_args()

    # config.py reads these at import time, so set them before importing the app
    data_dir = tempfile.mkdtemp(prefix="wp-eval-")
    os.environ["WP_SEARCH_DATA"] = data_dir
    if args.model:
        os.environ["WP_SEARCH_MODEL"] = args.model
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    sys.path.insert(0, REPO_DIR)

    import database_creator as dc
    from config import META_PATH

    try:
        shutil.copy(args.articles, META_PATH)
        questions = load_jsonl(args.questions)
        known_ids = {a["id"] for a in dc.get_metadata()}
        for q in questions:
            missing = set(q["expected"]) - known_ids
            if missing:
                raise SystemExit(f"Expected ids {sorted(missing)} are not in the snapshot: {q['question']}")

        started = time.time()
        index = dc.get_faiss_index(None, "content")
        build_s = time.time() - started

        rows = []
        for q in questions:
            results = dc.querying_index(q["question"], index, k=args.k)
            ranked = [r["metadata"]["id"] for r in results]
            rows.append({**q, "ranked": ranked, "titles": [r["metadata"]["title"] for r in results], **score(q["expected"], ranked)})
    finally:
        shutil.rmtree(data_dir, ignore_errors=True)

    n = len(rows)
    totals = {m: sum(r[m] for r in rows) / n for m in ("recall", "hit", "rr")}
    titles = {a["id"]: a["title"] for a in load_jsonl(args.articles)}

    for r in rows:
        if args.quiet and r["recall"] == 1.0:
            continue
        mark = "✅" if r["recall"] == 1.0 else ("🟡" if r["hit"] else "❌")
        print(f"{mark} {r['question']}")
        if r["recall"] < 1.0:
            for i in r["expected"]:
                if i not in r["ranked"]:
                    print(f"     missed: {titles[i][:90]}")
            print(f"     got #1: {r['titles'][0][:90] if r['titles'] else '-'}")

    model = os.environ.get("WP_SEARCH_MODEL", dc.MODEL_NAME)
    k = args.k
    print(
        f"\nmodel {model} | {n} questions | {index.ntotal} chunks, built in {build_s:.0f}s\n"
        f"recall@{k} {totals['recall']:.3f} | hit@{k} {totals['hit']:.3f} | MRR {totals['rr']:.3f}"
    )

    passed = args.min_recall is None or totals["recall"] >= args.min_recall
    if args.min_recall is not None:
        print(f"{'PASS' if passed else 'FAIL'}: recall@{k} {totals['recall']:.3f} (minimum {args.min_recall})")

    if args.summary:
        with open(args.summary, "a", encoding="utf-8") as f:
            f.write(f"### Retrieval eval: `{model}`\n\n")
            f.write(f"| recall@{k} | hit@{k} | MRR | questions | chunks |\n|---|---|---|---|---|\n")
            f.write(f"| {totals['recall']:.3f} | {totals['hit']:.3f} | {totals['rr']:.3f} | {n} | {index.ntotal} |\n\n")
            misses = [r for r in rows if r["recall"] < 1.0]
            if misses:
                f.write("<details><summary>Questions not fully answered</summary>\n\n")
                for r in misses:
                    f.write(f"- {r['question']} (recall {r['recall']:.2f})\n")
                f.write("\n</details>\n\n")

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
