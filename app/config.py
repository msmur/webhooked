import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")
API_KEY = os.getenv("API_KEY")
APP_ENVIRONMENT = os.getenv("APP_ENVIRONMENT")
IS_DEVELOPMENT = APP_ENVIRONMENT == "DEVELOPMENT"
