import requests
from typing import Dict, Any

class SubmissionHandler:
    def submit_answers(self, submission_url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submits the generated answer payload to the specified submission URL
        and returns the full JSON response.
        """
        print(f"Submitting payload to: {submission_url}")
        print(f"Payload: {payload}")
        try:
            response = requests.post(submission_url, json=payload, timeout=25)
            response.raise_for_status()

            print(f"Submission successful. Status code: {response.status_code}")
            # Return the full JSON response, as it may contain the next URL
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"An error occurred during answer submission: {e}")
            return {"error": f"Failed to submit answers: {str(e)}"}
        except ValueError: # Catches JSON decoding errors
            print(f"Could not decode JSON from response. Response text: {response.text[:200]}")
            return {"error": "Failed to decode JSON response from submission server."}

# Example of how this might be used:
if __name__ == "__main__":
    handler = SubmissionHandler()
    mock_url = "https://httpbin.org/post"
    mock_payload = {
      "email": "test@example.com",
      "secret": "secret",
      "url": "http://example.com/quiz-123",
      "answer": 42
    }
    result = handler.submit_answers(mock_url, mock_payload)
    print(result)
