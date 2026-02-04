import hashlib
import time
import requests
from config import API_BASE_URL, API_ENDPOINT, API_TOKEN, MAX_RETRIES, RETRY_DELAY_SECONDS


class APIClient:
    """
    Client for interacting with the EnergyGrid Mock API
    """

    def __init__(self):
        self.base_url = API_BASE_URL
        self.endpoint = API_ENDPOINT
        self.token = API_TOKEN
        self.full_url = f"{self.base_url}{self.endpoint}"

    def generate_signature(self, timestamp):
        string_to_hash = self.endpoint + self.token + timestamp
        signature = hashlib.md5(string_to_hash.encode()).hexdigest()
        return signature

    def fetch_devices(self, serial_numbers):
        if len(serial_numbers) > 10:
            raise ValueError("Batch size cannot exceed 10 devices")

        timestamp = str(int(time.time() * 1000))
        signature = self.generate_signature(timestamp)

        headers = {
            "Content-Type": "application/json",
            "timestamp": timestamp,
            "signature": signature
        }

        payload = {
            "sn_list": serial_numbers
        }

        for attempt in range(MAX_RETRIES):
            try:
                response = requests.post(
                    self.full_url,
                    json=payload,
                    headers=headers,
                    timeout=10
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    time.sleep(RETRY_DELAY_SECONDS)
                elif response.status_code == 401:
                    raise Exception(f"Authentication failed: {response.json()}")
                else:
                    raise Exception(f"Request failed: {response.status_code}")

            except requests.exceptions.RequestException as e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY_SECONDS)
                else:
                    raise Exception(f"Failed after {MAX_RETRIES} retries: {e}")

        raise Exception("Request failed after all retries")

    def test_connection(self):
        try:
            result = self.fetch_devices(["SN-000"])
            print("Connection successful")
            print(result["data"][0])
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
