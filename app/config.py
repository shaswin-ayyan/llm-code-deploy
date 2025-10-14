import os
from dotenv import load_dotenv

load_dotenv()

DEPLOYMENT_SECRET = os.getenv("DEPLOYMENT_SECRET")
MOCK_MODE = os.getenv("MOCK_MODE", "True").lower() in ("true", "1", "t")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USER = os.getenv("GITHUB_USER")
