from pdfminer.high_level import extract_text


def get_text(file_path):
    text = extract_text(file_path)
    return text