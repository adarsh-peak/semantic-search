import pdfplumber
from fastapi import UploadFile

def dict_to_text(d, prefix=""):
    lines = []
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            lines.extend(dict_to_text(v, key))
        elif isinstance(v, list):
            for i, item in enumerate(v):
                lines.extend(dict_to_text(item, f"{key}[{i}]"))
        else:
            lines.append(f"{key}: {v}")
    return "\n".join(lines)

def pdf_to_text(file: UploadFile) -> str:
    with pdfplumber.open(file.file) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)
