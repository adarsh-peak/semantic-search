from app.configs.constants import CHUNK_FIELD_MAP
from typing import Dict
import json
import csv
import io
import ast
from fastapi import UploadFile

class DataPartitioning:
  @staticmethod
  def group_based_on_context(company: dict):
    company_id = company.get("id")
    company_name = company.get("Company Name")
    chunks = []

    for chunk_type, field_list in CHUNK_FIELD_MAP.items():
        text = DataPartitioning.format_chunk_text(chunk_type, company)
        if text:
            chunks.append({
                "company_id": company_id,
                "company_name": company_name,
                "chunk_type": chunk_type,
                "text": text
            })

    return chunks

  @staticmethod
  def convert_to_single_data(file: UploadFile):
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
  
  @staticmethod
  def read_csv_file(file: UploadFile):
    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))

    return reader
  
  @staticmethod
  def format_chunk_text(chunk_type: str, fields: Dict[str, str]) -> str:
    """
    helper for chunk partion
    """
    def format_value(k: str, v: str) -> str:
        if not v:
            return ""
        if "Round" in k or "Date" in k:
            return f"{k.replace('_', ' ')}: {v[:10]}"
        if "Funding" in k or "Money" in k or "FMV" in k or "Amount" in k or "Ownership" in k:
            return f"{k.replace('_', ' ')}: ${v}M" if v else ""
        return f"{k.replace('_', ' ')}: {v}"

    if chunk_type == "team":
        # Handle founders separately
        founders = []
        try:
            if fields.get("Founders"):
                founders = json.loads(fields.get("Founders", "[]"))
        except Exception:
            founders = []

        founder_text = ", ".join(f"{f['name']} ({f['role']})" for f in founders if f.get("name"))
        deal_team = fields.get("Deal Team Members", "")

        lines = []
        if founder_text:
            lines.append(f"Founders: {founder_text}.")
        if deal_team:
            lines.append(f"Deal Team Members: {deal_team}.")
        return " ".join(lines)

    lines = [format_value(k, fields[k]) for k in CHUNK_FIELD_MAP[chunk_type] if k in fields and fields[k]]
    return " ".join(lines).strip()
  