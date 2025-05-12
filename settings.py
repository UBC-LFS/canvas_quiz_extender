"""
This file is responsible for accessing variables in the .env and making them available globally
"""

from dotenv import load_dotenv
import os

load_dotenv(override=True)

API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")
