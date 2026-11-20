
import requests
import time
import getpass
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

API_KEY = os.getenv("SMALLEST_API_KEY") or getpass.getpass("Enter your Smallest API key: ")

url = "https://api.smallest.ai/waves/v1/tts"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "audio/wav"
}

payload = {
    "text": "Hello, this is my first API quality test with Smallest AI.",
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
        timeout=(10, 60)
    )

    elapsed = time.perf_counter() - start

    print("\n--- TTS API TEST ---")
    print("Status:", response.status_code)
    print("Response time:", round(elapsed * 1000, 2), "ms")
    print("Content-Type:", response.headers.get("Content-Type"))
    print("Request ID:", response.headers.get("x-request-id", "Not provided"))

    if response.ok:
        with open("tts_test.wav", "wb") as file:
            file.write(response.content)

        print("Audio saved: tts_test.wav")
        print("Audio size:", len(response.content), "bytes")
    else:
        print("Error response:", response.text[:2000])

except requests.exceptions.Timeout:
    print("Request timed out")

except requests.exceptions.RequestException as error:
    print("Connection error:", str(error))
