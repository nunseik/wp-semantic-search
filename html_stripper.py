from html.parser import HTMLParser

# Tags that end a block of text: a line break is kept there so paragraphs stay apart.
BLOCK_TAGS = {
    "p", "div", "br", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6",
    "blockquote", "figure", "figcaption", "section", "article", "table", "tr", "pre",
}
SKIP_TAGS = {"script", "style"}


class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.skipping = 0

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self.skipping += 1
        elif tag == "br":
            self.text_parts.append("\n")

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS:
            self.skipping = max(0, self.skipping - 1)
        elif tag in BLOCK_TAGS:
            self.text_parts.append("\n")

    def handle_data(self, data):
        if not self.skipping:
            self.text_parts.append(data)

    def get_data(self):
        lines = (" ".join(line.split()) for line in "".join(self.text_parts).splitlines())
        return "\n".join(line for line in lines if line)


def strip_html(html):
    stripper = HTMLStripper()
    stripper.feed(html)
    stripper.close()
    return stripper.get_data()


def get_stripped_content(raw_data, fields_to_clean):
    """Replace each field in fields_to_clean with its plain text (WordPress sends {"rendered": html})."""
    if isinstance(fields_to_clean, str):
        fields_to_clean = [fields_to_clean]

    list_dict = []
    for row in raw_data:
        for field in fields_to_clean:
            if field not in row:
                continue
            value = row[field]
            if isinstance(value, dict) and "rendered" in value:
                value = value["rendered"]
            row[field] = strip_html(str(value))
        list_dict.append(row)

    return list_dict
