import os
import requests
import json
import pandas as pd
from pypdf import PdfReader
from io import BytesIO
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
        data = { "model": model, "prompt": prompt, "max_tokens": max_tokens }
        try:
            response = requests.post(endpoint, headers=self.headers, json=data, timeout=45)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

class AIOrchestrator:
    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        self.llm_client = RealLLMClient(api_key=api_key)
        self.model = "gpt-4.1-nano"

    def construct_answer_payload(self, scraped_data: Dict, email: str, secret: str, url: str) -> Dict:
        full_context = "\n".join(scraped_data.get("hidden_data", []))

        # 1. First LLM call: Parse instructions
        instruction_prompt = f"""
        Parse the following text to identify the core task, any file URLs, the submission URL, and the required JSON format for the answer.
        Return a JSON object with keys: 'task', 'file_url', 'submission_url', 'json_format'.

        Context:
        {full_context}
        """
        parsed_instructions = self._get_llm_json_response(instruction_prompt, 500)

        # 2. Handle files if any
        file_content = ""
        if parsed_instructions.get("file_url"):
            file_content = self._download_and_process_file(parsed_instructions["file_url"])

        # 3. Second LLM call: Solve the task
        solver_prompt = f"""
        You are a data science expert. Solve the following task.
        Task: {parsed_instructions.get('task')}
        File Content:
        {file_content[:3000]}

        Provide only the final answer.
        """
        answer = self._get_llm_response(solver_prompt, 200)

        # 4. Construct the final JSON payload
        final_payload = self._build_payload(parsed_instructions.get("json_format", {}), email, secret, url, answer)
        return final_payload

    def _download_and_process_file(self, url: str) -> str:
        try:
            response = requests.get(url)
            response.raise_for_status()
            if "pdf" in url:
                reader = PdfReader(BytesIO(response.content))
                return "\n".join(page.extract_text() for page in reader.pages)
            elif "csv" in url:
                return pd.read_csv(BytesIO(response.content)).to_string()
            else:
                return response.text
        except Exception as e:
            return f"Error processing file: {e}"

    def _build_payload(self, json_format: Dict, email: str, secret: str, url:str, answer: Any) -> Dict:
        # A simple approach to fill the format. Can be made more robust.
        payload = json.loads(json_format) if isinstance(json_format, str) else json_format
        payload['email'] = email
        payload['secret'] = secret
        payload['url'] = url
        payload['answer'] = self._cast_answer(answer)
        return payload

    def _cast_answer(self, answer: str):
        answer = answer.strip()
        if answer.lower() == 'true': return True
        if answer.lower() == 'false': return False
        try: return int(answer)
        except ValueError:
            try: return float(answer)
            except ValueError: return answer

    def _get_llm_json_response(self, prompt: str, max_tokens: int) -> Dict:
        response_text = self._get_llm_response(prompt, max_tokens)
        try:
            # Clean the text to ensure it's valid JSON
            json_str = response_text[response_text.find('{'):response_text.rfind('}')+1]
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {"error": "Failed to decode LLM JSON response."}

    def _get_llm_response(self, prompt: str, max_tokens: int) -> str:
        response = self.llm_client.create_completion(self.model, prompt, max_tokens)
        if "error" in response: return f"Error from LLM: {response['error']}"
        try:
            return response['choices'][0]['text'].strip()
        except (KeyError, IndexError):
            return "Error: Could not parse answer from LLM response."
