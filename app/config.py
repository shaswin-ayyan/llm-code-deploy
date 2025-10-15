import os
from dotenv import load_dotenv

# Load environment variables
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
load_dotenv(env_path)

# AIPipe Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AIPIPE_EMAIL = os.getenv("AIPIPE_EMAIL")

# Other configurations
DEPLOYMENT_SECRET = os.getenv("DEPLOYMENT_SECRET")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USER = os.getenv("GITHUB_USER")
MOCK_MODE = os.getenv("MOCK_MODE", "False").lower() in ("true", "1", "t")

# Validation
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is required")
if not AIPIPE_EMAIL and not MOCK_MODE:
    print("⚠️  AIPIPE_EMAIL is recommended for AIPipe service")

print(f"✅ AIPipe configured for: {AIPIPE_EMAIL}")