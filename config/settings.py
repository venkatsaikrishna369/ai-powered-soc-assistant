import os
from typing import Dict, Any

# API Keys Configuration
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Application Settings
APP_NAME = "Network Security Intelligence Dashboard"
VERSION = "1.0.0"
DEBUG = True
HOST = "127.0.0.1"
PORT = 8000

# Path Settings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
MODELS_DIR = os.path.join(BASE_DIR, "ml", "models")

# Dataset Paths
TRAINING_DATA_PATH = os.path.join(RAW_DATA_DIR, "training.csv")
TESTING_DATA_PATH = os.path.join(RAW_DATA_DIR, "testing.csv")

# ... rest of the settings ...