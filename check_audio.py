
import wave

with wave.open("sample.wav", "rb") as audio:
    print("Channels:", audio.getnchannels())
    print("Sample rate:", audio.getframerate())
    print("Sample width:", audio.getsampwidth(), "bytes")
    print("Frames:", audio.getnframes())
    print("Duration:", round(
        audio.getnframes() / audio.getframerate(), 2
    ), "seconds")
