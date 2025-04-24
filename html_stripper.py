from html.parser import HTMLParser

class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []

    def handle_data(self, data):
        self.text_parts.append(data)

    def get_data(self):
        return ''.join(self.text_parts)

def strip_html(html):
    stripper = HTMLStripper()
    stripper.feed(html)
    return stripper.get_data()

def get_stripped_content(raw_data, field_to_clean):
    list_dict = []

    for row in raw_data:
        html_dict = row[field_to_clean]
        if isinstance(html_dict, dict) and "rendered" in html_dict:
            row[field_to_clean] = strip_html(html_dict["rendered"])
        else:
            row[field_to_clean] = strip_html(str(html_dict))
        list_dict.append(row)

    return list_dict