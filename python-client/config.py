import os
from dotenv import load_dotenv
load_dotenv()
API_BASE_URL = "http://localhost:3000"
API_ENDPOINT = "/device/real/query"
API_TOKEN = os.getenv("API_TOKEN")

TOTAL_DEVICES = 500
BATCH_SIZE = 10

RATE_LIMIT_SECONDS = 1.0

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2.0

OUTPUT_DIR = "output"
OUTPUT_FILENAME = "aggregated_data.json"
