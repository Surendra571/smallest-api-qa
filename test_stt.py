
import requests
import time
import getpass
import json
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

url = os.getenv("SMALLEST_STT_REST_URL") or "https://api.smallest.ai/waves/v1/stt/?model=pulse&language=en"

api_key = os.getenv("SMALLEST_API_KEY") or getpass.getpass("Enter your Smallest API key: ")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "url": "https://github.com/smallest-inc/cookbook/raw/main/speech-to-text/getting-started/samples/audio.wav"
}

try:
    start = time.perf_counter()

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=(10, 60)
    )

    elapsed = time.perf_counter() - start

    print("\n--- STT API TEST ---")
    print("Status:", response.status_code)
    print("Response time:", round(elapsed * 1000, 2), "ms")
    print("Content-Type:", response.headers.get("Content-Type"))
    print("Request ID:", response.headers.get("x-request-id"))

    try:
        result = response.json()
        print("Response:")
        print(json.dumps(result, indent=2))
    except ValueError:
        print("Non-JSON response:", response.text[:2000])

except requests.exceptions.RequestException as error:
    print("Request failed:", error)
