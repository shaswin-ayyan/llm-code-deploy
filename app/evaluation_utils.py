import requests
import time
from typing import Dict

def notify_evaluation_service(evaluation_url: str, data: Dict, max_retries: int = 5):
    """
    Notify evaluation service with exponential backoff
    """
    for attempt in range(max_retries):
        try:
            response = requests.post(
                evaluation_url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ Evaluation service notified successfully (attempt {attempt + 1})")
                return True
            else:
                print(f"⚠️ Evaluation service returned {response.status_code}: {response.text}")
                
        except requests.RequestException as e:
            print(f"⚠️ Evaluation service connection failed (attempt {attempt + 1}): {e}")
        
        # Exponential backoff
        if attempt < max_retries - 1:
            delay = 2 ** attempt
            print(f"🔄 Retrying in {delay} seconds...")
            time.sleep(delay)
    
    print("❌ All evaluation service notification attempts failed")
    return False