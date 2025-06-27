from ollama import chat
from typing import List, Dict, Any
from app.configs.constants import LLMConstant
import re
import json

class SemanticSearchLLM:
    def __init__(self, model_name: str = LLMConstant.model):
        """
        Initialize the semantic search + LLM wrapper.
        :param model_name: Name of the local model pulled in Ollama.
        """
        self.model_name = model_name

    def generate_prompt(self, question: str, context_chunks: List[str]) -> str:
        """
        Create a prompt for the LLM using retrieved context and user question.
        """
        context = "\n".join(context_chunks)
        prompt = f"""
          You are a helpful assistant answering questions based on the provided context.

          Context:
          {context}

          Question: {question}

          Answer:"""
        return prompt.strip()

    def query_llm(self, prompt: str) -> str:
        """
        Send the prompt to the local LLM via Ollama and return the response.
        """
        response = chat(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        return response['message']['content']

    def answer_question(self, question: str, retrieved_chunks: List[str]) -> str:
        """
        High-level method to answer a question using the context and LLM.
        """
        prompt = self.generate_prompt(question, retrieved_chunks)
        return self.query_llm(prompt)

    def extract_query_and_filters(self, user_query: str) -> Dict[str, Any]:
        prompt = f"""
                You are a helpful assistant that generates Elasticsearch-compatible query filters from a user's natural language request.

                Given the user query: "{user_query}"

                Return a JSON object with:
                1. "query_text": cleaned string for semantic embedding search.
                2. "es_filter": a valid Elasticsearch query fragment (under `bool -> filter`) using:
                - `term` or `terms` for categorical filters
                - `range` for numeric/date filters
                - `term` with boolean for true/false
                - keyword fields for string match (e.g., "Geo.keyword")

                Only include fields from:
                ["Geo", "Sectors", "Status", "Type", "Investment Type", "Location", "Program", "Deal Team Members", "Founders",
                "PXV Ownership", "PXV Last Round", "Total PXV Funding", "Latest FMV", "Latest Post Money", "First Round",
                "Last Round", "PXV First Round", "PXV Last Round Amount", "Stealth"]

                Example output:
                {{
                "query_text": "AI startups in health sector",
                "es_filter": {{
                    "bool": {{
                    "filter": [
                        {{ "term": {{ "Geo.keyword": "India" }} }},
                        {{ "term": {{ "Sectors.keyword": "health" }} }},
                        {{ "range": {{ "First Round": {{ "gt": "2020-01-01" }} }} }}
                    ]
                    }}
                }}
                }}
            """



        try:
            response = self.query_llm(prompt)
            parsed = self.extract_json_from_response(response)
            return parsed
        except Exception as e:
            print(f"[LLM Filter Extraction Error]: {e}")
            return {"query_text": user_query, "filters": {}}

    def extract_json_from_response(self, response: str) -> dict:
        try:
            # Use regex to extract the first valid JSON object from the response
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if not match:
                raise ValueError("No JSON object found in response")

            json_str = match.group(0)
            parsed = json.loads(json_str)
            return parsed

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON from LLM response: {e}")

        except Exception as e:
            raise RuntimeError(f"Unexpected error parsing LLM response: {e}")