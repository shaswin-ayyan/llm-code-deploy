import requests
import time
from . import config

def notify_evaluation(evaluation_url: str, payload: dict):
    """
    Sends a POST request to the evaluation URL with the deployment details.
    Includes retry logic with exponential backoff.
    """
    max_retries = 5
    delay = 1  # initial delay in seconds

    for attempt in range(max_retries):
        if config.MOCK_MODE:
            print(f"MOCK_MODE: Simulating POST to {evaluation_url} (Attempt {attempt + 1})")
            print(f"Payload: {payload}")
            return {
                "mocked": True,
                "endpoint": evaluation_url,
                "status": 200,
                "response": {"message": "Evaluation notification received."}
            }

        # Real implementation
        try:
            print(f"Sending POST to {evaluation_url} (Attempt {attempt + 1})")
            response = requests.post(evaluation_url, json=payload, timeout=10)

            if response.status_code == 200:
                print("Successfully notified evaluation server.")
                return response.json()
            else:
                print(f"Evaluation server returned status {response.status_code}. Retrying...")

        except requests.RequestException as e:
            print(f"Request to evaluation server failed: {e}. Retrying...")

        # Wait before the next retry
        if attempt < max_retries - 1:
            print(f"Waiting {delay} seconds before next retry.")
            time.sleep(delay)
            delay *= 2 # Exponential backoff

    # If all retries fail, raise an exception
    raise requests.RequestException(f"Failed to notify evaluation server at {evaluation_url} after {max_retries} attempts.")
