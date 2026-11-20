
import asyncio
import getpass
import json
import os
import time
import wave

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import websockets
from urllib.parse import urlencode

AUDIO_FILE = "sample.wav"
SAMPLE_RATE = 24000
CHUNK_SIZE = 4096

BASE_URL = "wss://api.smallest.ai/waves/v1/stt/live?model=pulse"

params = {
    "language": "en",
    "encoding": "linear16",
    "sample_rate": str(SAMPLE_RATE),
    "word_timestamps": "true"
}

WS_URL = f"{BASE_URL}&{urlencode(params)}"


async def main():
    api_key = os.getenv("SMALLEST_API_KEY") or getpass.getpass("Enter your Smallest API key: ")

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    print("\n--- STT WEBSOCKET TEST ---")

    start = time.perf_counter()
    transcripts = []

    try:
        async with websockets.connect(
            WS_URL,
            additional_headers=headers,
            open_timeout=15,
            close_timeout=10
        ) as ws:

            print("Connection: Established")

            with wave.open(AUDIO_FILE, "rb") as audio:
                if audio.getnchannels() != 1:
                    raise ValueError("Audio must be mono")

                if audio.getframerate() != SAMPLE_RATE:
                    raise ValueError("Sample rate must be 24000 Hz")

                if audio.getsampwidth() != 2:
                    raise ValueError("Audio must be 16-bit PCM")

                while True:
                    chunk = audio.readframes(CHUNK_SIZE // 2)

                    if not chunk:
                        break

                    await ws.send(chunk)

            print("Audio: Sent successfully")

            await ws.send(json.dumps({
                "type": "close_stream"
            }))

            print("Stream: Closed by client")

            try:
                while True:
                    message = await asyncio.wait_for(
                        ws.recv(),
                        timeout=10
                    )

                    if isinstance(message, bytes):
                        print("Received binary response")
                        continue

                    data = json.loads(message)

                    print("Event:", json.dumps(data))

                    if data.get("is_final") and data.get("transcript"):
                        transcripts.append(data["transcript"])

                    if data.get("is_last"):
                        break

            except asyncio.TimeoutError:
                print("No more events received within timeout")

        elapsed = time.perf_counter() - start

        print("\n--- RESULTS ---")
        print("Total time:", round(elapsed * 1000, 2), "ms")
        print("Transcript events:", len(transcripts))
        print("Combined transcript:", " ".join(transcripts))

    except Exception as error:
        print("WebSocket test failed:", type(error).__name__, str(error))


if __name__ == "__main__":
    asyncio.run(main())
