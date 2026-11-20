
import asyncio
import json
import os
import wave
import getpass
import websockets

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

WS_URL = (
    "wss://api.smallest.ai/waves/v1/stt/live"
    "?model=pulse&language=en&encoding=linear16"
    "&sample_rate=24000&word_timestamps=true"
)

AUDIO_FILE = "sample.wav"
CHUNK_SIZE = 4096


async def main():
    api_key = os.getenv("SMALLEST_API_KEY") or getpass.getpass("Enter your Smallest API key: ")
    headers = {"Authorization": f"Bearer {api_key}"}

    # Read raw PCM frames, excluding the WAV header.
    with wave.open(AUDIO_FILE, "rb") as audio:
        audio_bytes = audio.readframes(audio.getnframes())

    print("\n--- PHASE 1: SIMULATE INTERRUPTION ---")

    # Start a connection and send only a small part of the audio.
    ws = await websockets.connect(
        WS_URL, additional_headers=headers
    )
    print("First connection established")

    await ws.send(audio_bytes[:CHUNK_SIZE])
    print(f"Sent {CHUNK_SIZE} bytes")

    # Close with an abnormal code to simulate interruption.
    await ws.close(code=1011, reason="QA interruption test")
    print("First connection closed intentionally")

    print("\n--- PHASE 2: CONNECT AGAIN ---")

    transcripts = []
    session_id = None

    try:
        async with websockets.connect(
            WS_URL, additional_headers=headers
        ) as ws:
            print("Fresh connection established")

            # Send the complete audio in the new session.
            for offset in range(0, len(audio_bytes), CHUNK_SIZE):
                chunk = audio_bytes[offset:offset + CHUNK_SIZE]
                await ws.send(chunk)
                await asyncio.sleep(0.05)

            await ws.send(json.dumps({"type": "close_stream"}))
            print("Complete audio sent")

            async for message in ws:
                data = json.loads(message)

                session_id = data.get("session_id", session_id)

                if data.get("is_final") and data.get("transcript"):
                    transcripts.append(data["transcript"])

                if data.get("is_last"):
                    break

        final_text = " ".join(" ".join(transcripts).split())

        print("\n--- RESULTS ---")
        print("Session ID:", session_id)
        print("Final transcript:", final_text)
        print("Final segments received:", len(transcripts))

    except Exception as error:
        print("Reconnect test failed:", type(error).__name__, str(error))


if __name__ == "__main__":
    asyncio.run(main())
