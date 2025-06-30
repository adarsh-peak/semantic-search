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
    ownership = company.get("PXV Ownership")
    total_funding = company.get("Total PXV Funding")
    last_round_amt = company.get("PXV Last Round Amount")
    latest_fmv = company.get("Latest FMV")
    latest_post_money = company.get("Latest Post Money")
    first_round = company.get("PXV First Round")
    last_round = company.get("PXV Last Round")
    first_investment = company.get("First Round")
    last_investment = company.get("Last Round")
    chunks = []

    for chunk_type, field_list in CHUNK_FIELD_MAP.items():
        text = DataPartitioning.format_chunk_text(chunk_type, company)
        if text:
            chunks.append({
                "company_id": company_id,
                "company_name": company_name,
                "chunk_type": chunk_type,
                "pxv_ownership": ownership,
                "total_pvx_funding": total_funding,
                "pxv_last_round_amount": last_round_amt,
                "latest_fmv": latest_fmv,
                "latest_post_money": latest_post_money,
                "first_round_date": first_investment,
                "last_round_date": last_investment,
                "pxv_first_round_date": first_round,
                "pxv_last_round_date": last_round,
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
    Converts chunk data into natural language summaries for embedding.
    """
    def clean(v):
        return v.strip() if isinstance(v, str) else v

    if chunk_type == "basic_info":
        parts = []

        name = clean(fields.get("Company Name"))
        geo = clean(fields.get("Geo"))
        status = clean(fields.get("Status"))
        type_ = clean(fields.get("Type"))
        location = clean(fields.get("Location"))
        stealth = clean(fields.get("Stealth"))
        sectors = clean(fields.get("Sectors"))
        founders = clean(fields.get("Founders"))
        reviewers = clean(fields.get("PXV Partners/Reviewer"))
        strategy = clean(fields.get("Strategy"))
        program = clean(fields.get("Program"))
        deal_team = clean(fields.get("Deal Team Members"))

        if name:
            parts.append(f"{name} is a {type_} company based in {geo}.")
        if status:
            parts.append(f"It is currently {status.lower()}.")
        if stealth and stealth.upper() == "TRUE":
            parts.append("The company is in stealth mode.")
        if sectors:
            parts.append(f"It operates in the {sectors} sector.")
        if founders:
            parts.append(f"It was founded by {founders}.")
        if deal_team:
            parts.append(f"Deal team members include {deal_team}.")
        if reviewers:
            parts.append(f"PXV reviewers for the company include {reviewers}.")
        if strategy:
            parts.append(f"The company's strategy is: {strategy}.")
        if program:
            parts.append(f"It is part of the {program} program.")

        return " ".join(parts)

    elif chunk_type == "investment":
        parts = []

        def fmt_money(label, val):
            return f"{label} was ${val}M." if val else ""

        def fmt_date(label, val):
            return f"{label} was on {val[:10]}." if val else ""

        ownership = clean(fields.get("PXV Ownership"))
        total_funding = clean(fields.get("Total PXV Funding"))
        last_round_amt = clean(fields.get("PXV Last Round Amount"))
        latest_fmv = clean(fields.get("Latest FMV"))
        latest_post_money = clean(fields.get("Latest Post Money"))
        first_round = clean(fields.get("PXV First Round"))
        last_round = clean(fields.get("PXV Last Round"))
        first_investment = clean(fields.get("First Round"))
        last_investment = clean(fields.get("Last Round"))

        if ownership:
            parts.append(f"PXV owns {ownership}% of the company.")
        if total_funding:
            parts.append(fmt_money("Total PXV funding", total_funding))
        if last_round_amt:
            parts.append(fmt_money("The last round amount", last_round_amt))
        if latest_fmv:
            parts.append(fmt_money("The latest FMV", latest_fmv))
        if latest_post_money:
            parts.append(fmt_money("The latest post-money valuation", latest_post_money))
        if first_round:
            parts.append(fmt_date("PXV first participated", first_round))
        if last_round:
            parts.append(fmt_date("PXV last participated", last_round))
        if first_investment:
            parts.append(fmt_date("The company’s first funding round", first_investment))
        if last_investment:
            parts.append(fmt_date("The last funding round", last_investment))

        return " ".join(parts)

    else:
        return ""

  