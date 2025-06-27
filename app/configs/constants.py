class EmbeddingConstant:
  model: str = "all-MiniLM-L6-v2"
  dims: int = 384
  
class ElasticConstant:
  index_name: str = "company-384"
  
class LLMConstant:
  model: str = "mistral"
  
CHUNK_FIELD_MAP = {
    "basic_info": [
        "Company Name", "Type", "Status", "Geo", "Location", "Sectors", "Stealth"
    ],
    "pxv_investment_summary": [
        "PXV First Round", "PXV Last Round", "PXV Ownership",
        "Total PXV Funding", "PXV Last Round Amount"
    ],
    "funding_snapshot": [
        "Latest Post Money", "Latest FMV", "First Round", "Last Round"
    ],
    "strategy": [
        "Strategy", "PXV Partners/Reviewer", "Funds", "Program"
    ],
    "team": [
        "Founders", "Deal Team Members"
    ]
}
