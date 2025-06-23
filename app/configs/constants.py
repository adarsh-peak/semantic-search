class EmbeddingConstant:
  model: str = "all-mpnet-base-v2"
  dims: int = 768
  
class ElasticConstant:
  index_name: str = "company"
  
class LLMConstant:
  model: str = "mistral"