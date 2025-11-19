import os
import requests
import json
from typing import Dict, Any

class RealLLMClient:
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1"):
        if not api_key:
            raise ValueError("API key is required.")
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def create_completion(self, model: str, prompt: str, max_tokens: int) -> Dict[str, Any]:
        endpoint = f"{self.base_url}/completions"
        data = {
            "model": model,
            "prompt": prompt,
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(endpoint, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error calling LLM API: {e}")
            return {"error": str(e)}

class AIOrchestrator:
    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")

        self.llm_client = RealLLMClient(api_key=api_key)
        self.model = "gpt-4.1-nano" # Or any other compatible model

    def solve_question(self, question_text: str, context: str) -> str:
        """
        Solves a single, specific question using the LLM.
        """
        prompt = f"""
        You are a data science expert. Based on the provided context, answer the following quiz question.
        Provide only the answer, without any explanation or pleasantries.

        Context:
        ---
        {context[:3500]}
        ---
        Question: {question_text}

        Answer:
        """

        print(f"Solving question: {question_text[:100]}...")
        response = self.llm_client.create_completion(
            model=self.model,
            prompt=prompt,
            max_tokens=150
        )

        if "error" in response:
            return f"Error from LLM: {response['error']}"

        try:
            # Extract the answer from the first choice
            answer = response['choices'][0]['text'].strip()
            print(f"LLM Answer: {answer}")
            return answer
        except (KeyError, IndexError) as e:
            print(f"Error parsing LLM response: {e}")
            return "Error: Could not parse answer from LLM response."
