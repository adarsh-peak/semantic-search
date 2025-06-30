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
            You are a helpful assistant that converts a user's natural language query into:
            1. A cleaned string to be used for semantic embedding search (based on the 'text' field)
            2. Optional Elasticsearch-compatible filters (on indexed fields)
            3. Optional sorting instructions if the user asks for rankings (e.g., "top funded", "highest ownership", "latest round")

            Given this user query: "{user_query}"

            You MUST return a strictly valid JSON object with the following structure:
            1. "query_text": cleaned version of the query for semantic vector search
            2. "es_filter": a valid Elasticsearch bool->filter query if relevant, or `null` if not applicable
            3. "sort_by": one of the allowed sortable fields below, or `null` if not relevant
            4. "sort_order": either "desc" or "asc" if sorting is applicable, otherwise `null`

            ✅ Allowed chunk_type values (only use these for filtering):
            - "basic_info"
            - "investment"

            ✅ Allowed metadata fields for filtering and sorting:
            - "chunk_type" (keyword, use "term")
            - "company_id" (keyword, use "term")
            - "company_name" (text, use "match")
            - "pxv_ownership" (float)
            - "total_pvx_funding" (float)
            - "pxv_last_round_amount" (float)
            - "latest_fmv" (float)
            - "latest_post_money" (float)
            - "first_round_date" (date)
            - "last_round_date" (date)
            - "pxv_first_round_date" (date)
            - "pxv_last_round_date" (date)

            ⚠️ DO NOT:
            - Invent or use any fields not listed above
            - Use both "term" and "terms" for the same field
            - Use `company_name` to match people (e.g., founders or reviewers)
            - Output invalid JSON — structure and syntax must be correct
            - Wrap the JSON in code blocks or markdown (no backticks)
            - Use any other chunk type apart from ["investment", "basic_info"]

            ✅ Examples:

            Input: "Which companies has PXV invested in recently?"
            Output:
            {{
            "query_text": "PXV recent investments",
            "es_filter": {{
                "bool": {{
                "filter": [
                    {{ "term": {{ "chunk_type": "investment" }} }}
                ]
                }}
            }},
            "sort_by": "pxv_last_round_date",
            "sort_order": "desc"
            }}

            Input: "List companies with highest PXV ownership"
            Output:
            {{
            "query_text": "companies with highest PXV ownership",
            "es_filter": {{
                "bool": {{
                "filter": [
                    {{ "term": {{ "chunk_type": "investment" }} }}
                ]
                }}
            }},
            "sort_by": "pxv_ownership",
            "sort_order": "desc"
            }}

            Input: "What does Equilibrium do?"
            Output:
            {{
            "query_text": "Equilibrium description",
            "es_filter": {{
                "bool": {{
                "filter": [
                    {{ "term": {{ "chunk_type": "basic_info" }} }},
                    {{ "match": {{ "company_name": "Equilibrium" }} }}
                ]
                }}
            }},
            "sort_by": null,
            "sort_order": null
            }}

            If filtering or sorting is not applicable for the query, use `null` for "es_filter", "sort_by", and "sort_order".
            """



        try:
            response = self.query_llm(prompt)
            print("response", response, flush=True)
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