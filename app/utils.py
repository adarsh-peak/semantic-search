import pdfplumber
from fastapi import UploadFile
import json
import csv
import ast
from typing import List
import io


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

"""
[Company Name] (ID: [id]) is a [Type] company focused on [Strategy], operating in the [Sectors] sector and located in [Location], [Geo]. 
It is currently [Status] and participating in the [Program] program. PXV has invested via [Funds] through an [Investment Type] investment. 
PXV owns [PXV Ownership] of the company. The first round PXV participated in was in [PXV First Round] with an amount of [PXV Last Round Amount], 
and the latest PXV round was [PXV Last Round]. The total PXV funding stands at [Total PXV Funding]. 
The latest FMV is [Latest FMV], and the post-money valuation is [Latest Post Money]. 
The deal team members were [Deal Team Members], and the company was reviewed by [PXV Partners/Reviewer]. 
Founders include [Founders]. Stealth mode: [Stealth].
"""

def row_to_text_full(values: list[str]) -> str:
    headers = [
        "id", "Company Name", "Strategy", "PXV Partners/Reviewer", "Funds", "Type", "Investment Type", "Status",
        "PXV Ownership", "PXV Last Round", "Total PXV Funding", "Latest FMV", "Latest Post Money", "First Round",
        "Last Round", "PXV First Round", "PXV Last Round Amount", "Stealth", "Geo", "Sectors", "Location",
        "Program", "Deal Team Members", "Founders"
    ]

    row = dict(zip(headers, values))

    return (
        f"{row['Company Name']} (ID: {row['id']}) is a {row['Type']} company focused on {row['Strategy']}, "
        f"operating in the {row['Sectors']} sector and located in {row['Location']}, {row['Geo']}. "
        f"It is currently {row['Status']} and participating in the {row['Program']} program. "
        f"PXV has invested via {row['Funds']} through an {row['Investment Type']} investment. "
        f"PXV owns {row['PXV Ownership']} of the company. The first round PXV participated in was in {row['PXV First Round']} "
        f"with an amount of {row['PXV Last Round Amount']}, and the latest PXV round was {row['PXV Last Round']}. "
        f"The total PXV funding stands at {row['Total PXV Funding']}. The latest FMV is {row['Latest FMV']}, "
        f"and the post-money valuation is {row['Latest Post Money']}. "
        f"The deal team members were {row['Deal Team Members']}, and the company was reviewed by {row['PXV Partners/Reviewer']}. "
        f"Founders include {format_founders(row['Founders'])}. Stealth mode: {row['Stealth']}."
    )

def format_founders(founders: str) -> str:
    if not founders:
        return ""
    
    founders = json.loads(founders.replace("'", '"'))
    
    formatted = []
    for founder in founders:
        name = founder.get("name", "Unknown")
        role = founder.get("role", "No role specified")
        formatted.append(f"{name} ({role})")
    
    return ", ".join(formatted)

def parse_csv_to_summaries(file: UploadFile) -> List[str]:
    summaries = []
    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))

    for row in reader:
        founders_raw = row.get("Founders", "").strip()
        try:
            founders_list = ast.literal_eval(founders_raw)
            founders_str = ", ".join(f["name"] for f in founders_list if "name" in f)
        except Exception:
            founders_str = founders_raw

        summary = (
            f"{row['Company Name']} (ID: {row['id']}) is a {row['Type']} company focused on {row['Strategy']}, "
        f"operating in the {row['Sectors']} sector and located in {row['Location']}, {row['Geo']}. "
        f"It is currently {row['Status']} and participating in the {row['Program']} program. "
        f"PXV has invested via {row['Funds']} through an {row['Investment Type']} investment. "
        f"PXV owns {row['PXV Ownership']} of the company. The first round PXV participated in was in {row['PXV First Round']} "
        f"with an amount of {row['PXV Last Round Amount']}, and the latest PXV round was {row['PXV Last Round']}. "
        f"The total PXV funding stands at {row['Total PXV Funding']}. The latest FMV is {row['Latest FMV']}, "
        f"and the post-money valuation is {row['Latest Post Money']}. "
        f"The deal team members were {row['Deal Team Members']}, and the company was reviewed by {row['PXV Partners/Reviewer']}. "
            f"The founders are {founders_str if founders_str else 'Not available'}."
            f"Stealth mode: {row['Stealth']}."
        )

        summaries.append(summary)

    return summaries