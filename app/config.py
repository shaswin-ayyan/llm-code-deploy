import os
from dotenv import load_dotenv

# Load environment variables from the parent directory's .env file
load_dotenv()

# LLM Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Security Configuration
QUIZ_SECRET = os.getenv("QUIZ_SECRET")

# Validation
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is required in the environment.")

if not QUIZ_SECRET:
    print("⚠️  QUIZ_SECRET is not set. The application will not be secure.")

print("✅ Configuration loaded.")
