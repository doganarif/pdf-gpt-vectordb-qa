import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    # Azure OpenAI settings
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_API_VERSION = os.getenv("AZURE_API_VERSION", "2024-02-01")
    AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")

    # Qdrant settings
    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    QDRANT_HTTPS = os.getenv("QDRANT_HTTPS", "false").lower() == "true"

    # Application settings
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    ENABLE_HTTPS = os.getenv("ENABLE_HTTPS", "false").lower() == "true"
    MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", 16))
    PORT = int(os.getenv("PORT", 8000))

    ENABLE_CORS = os.getenv("ENABLE_CORS", "false").lower() == "true"

config = Config()