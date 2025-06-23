from ollama import chat
from typing import List
from app.configs.constants import LLMConstant

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
