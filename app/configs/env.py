from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class BaseConfig(BaseSettings):
  elastic_host: str = os.getenv("ELASTIC_HOST", "0.0.0.0")
  elastic_port: int = os.getenv("ELASTIC_PORT", 9200)
  

@lru_cache()
def get_settings():
    """
    get env
    """
    return BaseConfig()