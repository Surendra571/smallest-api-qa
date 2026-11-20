
import requests
import time

url = "https://api.smallest.ai/waves/v1/tts"

headers = {
    "Authorization": "Bearer INVALID_TEST_KEY_12345",
    "Content-Type": "application/json",
    "Accept": "audio/wav"
}

payload = {
    "text": "Testing invalid API authentication.",
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

    print("\n--- INVALID AUTH TEST ---")
    print("Status:", response.status_code)
    print("Response time:", round(elapsed * 1000, 2), "ms")
    print("Content-Type:", response.headers.get("Content-Type"))
    print("Request ID:", response.headers.get("x-request-id"))
    print("Response body:", response.text[:2000])

except requests.exceptions.RequestException as error:
    print("Request failed:", error)
