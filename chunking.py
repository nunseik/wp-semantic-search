from config import CHUNK_WORDS, CHUNK_OVERLAP


def chunk_text(text, max_words=CHUNK_WORDS, overlap=CHUNK_OVERLAP):
    """Split text into chunks of at most max_words words.

    Paragraphs (lines) are kept whole and packed together while they fit.
    A paragraph longer than max_words is cut into windows that overlap by
    `overlap` words, so a sentence on a boundary still appears whole in one chunk.
    """
    if not 0 <= overlap < max_words:
        raise ValueError("overlap must be between 0 and max_words - 1")

    chunks, current = [], []
    for line in text.splitlines():
        words = line.split()
        if not words:
            continue

        if len(words) > max_words:
            if current:
                chunks.append(current)
                current = []
            step = max_words - overlap
            for start in range(0, len(words), step):
                chunks.append(words[start:start + max_words])
                if start + max_words >= len(words):
                    break
            continue

        if current and len(current) + len(words) > max_words:
            chunks.append(current)
            current = []
        current.extend(words)

    if current:
        chunks.append(current)

    return [" ".join(chunk) for chunk in chunks]
