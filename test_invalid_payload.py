
import requests
import time
import getpass
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

url = os.getenv("SMALLEST_TTS_URL") or "https://api.smallest.ai/waves/v1/tts"

api_key = os.getenv("SMALLEST_API_KEY") or getpass.getpass("Enter your Smallest API key: ")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Intentionally invalid: empty text
payload = {
    "text": "",
    "voice_id": "meher",
    "model": "lightning_v3.1_pro",
    "sample_rate": 24000,
    "output_format": "wav"
}

try:
    start = time.perf_counter()

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=(10, 30)
    )

    elapsed = time.perf_counter() - start

    print("\n--- INVALID PAYLOAD TEST ---")
    print("Status:", response.status_code)
    print("Response time:", round(elapsed * 1000, 2), "ms")
    print("Content-Type:", response.headers.get("Content-Type"))
    print("Request ID:", response.headers.get("x-request-id"))

    if "application/json" in response.headers.get("Content-Type", ""):
        print("Response body:", response.text[:2000])
    else:
        print("Response body is not JSON")

except requests.exceptions.RequestException as error:
    print("Request failed:", error)
