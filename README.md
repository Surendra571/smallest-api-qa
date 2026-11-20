# Smallest AI API Quality Assurance & Test Suite

Comprehensive automated Quality Assurance (QA) and test suite for the **Smallest AI Waves** API, covering **Text-to-Speech (TTS)** and **Speech-to-Text (STT)** endpoints across REST and real-time WebSocket protocols.

---

## 📋 Table of Contents
- [Overview](#overview)
- [Architecture & Test Coverage](#architecture--test-coverage)
- [Repository Structure](#repository-structure)
- [Prerequisites & Installation](#prerequisites--installation)
- [Configuration & Authentication](#configuration--authentication)
- [Running the Tests](#running-the-tests)
  - [1. Audio Verification](#1-audio-verification)
  - [2. Text-to-Speech (TTS) Tests](#2-text-to-speech-tts-tests)
  - [3. Speech-to-Text (STT) Tests](#3-speech-to-text-stt-tests)
- [Test Matrix](#test-matrix)
- [Best Practices & Security](#best-practices--security)
- [Related Documents](#related-documents
- 
---

## 🔍 Overview

This test suite validates functional correctness, security/authentication enforcement, input validation, audio format compliance, latency, and streaming resilience for:
- **Smallest AI Waves TTS API (`/waves/v1/tts`)**: Low-latency neural speech synthesis.
- **Smallest AI Waves STT API (`/waves/v1/stt/`)**: Batch audio transcription via remote URL.
- **Smallest AI Waves STT Live WebSocket (`/waves/v1/stt/live`)**: Bidirectional streaming speech-to-text transcription with real-time word timestamps.

---

## 🧪 Architecture & Test Coverage

```
                            Smallest AI Platform
                                     │
           ┌─────────────────────────┴─────────────────────────┐
           ▼                                                   ▼
   Waves v1 TTS (REST)                                 Waves v1 STT
  https://api.smallest.ai/waves/v1/tts                ┌────────┴────────┐
           │                                          ▼                 ▼
   ┌───────┴───────┐                             REST API          WebSocket
   ▼               ▼                        (/waves/v1/stt/)    (/waves/v1/stt/live)
Happy Path     Negative Tests                         │                 │
(Synthesis)  • Missing Auth Header                    ▼                 ▼
             • Invalid API Token                 Batch Audio     • Real-time Streaming
             • Missing voice_id                  Transcription   • Connection Drops
             • Empty Payload (text: "")                          • Session Recovery
```

### Coverage Highlights
1. **Functional Audio Synthesis**: Validates successful WAV audio generation, payload parameter parsing (`voice_id`, `model`, `sample_rate`, `output_format`), and output file integrity.
2. **Security & Authentication**:
   - Verification of rejected requests when the `Authorization` header is completely absent (returns `401 Unauthorized`).
   - Verification of rejected requests when an invalid bearer token is supplied.
3. **Input Validation**:
   - Missing required field validation (omitted `voice_id`).
   - Boundary condition testing (empty string `text: ""`).
4. **Speech-to-Text Transcription**:
   - Single-shot REST batch inference using a hosted WAV file URL.
   - Low-latency real-time chunk streaming over WebSocket (`linear16`, 24kHz, mono).
5. **Streaming Resilience & Fault Tolerance**:
   - Simulates abrupt socket disconnects (code `1011`).
   - Verifies session recovery and fresh stream processing without lingering session state.
6. **Audio Validation**:
   - Verifies channel count, sampling rate, bit depth, and frame duration before streaming to the WebSocket endpoint.

---

## 📁 Repository Structure

```
smallest-api-qa/
│
├── .gitignore               # Git ignore rules for virtual environments, outputs, and secrets
├── requirements.txt         # Python dependencies (requests, websockets)
├── README.md                # Project documentation and test runner guide
├── qa-report.md             # Detailed QA execution report, test logs, and findings
│
├── check_audio.py           # Utility to inspect and validate sample audio metadata
├── sample.wav               # Test fixture: 24kHz, 16-bit Mono PCM audio file
├── tts_test.wav             # Generated test artifact from successful TTS synthesis
│
├── test_tts.py              # Functional test: Baseline TTS synthesis (Happy Path)
├── test_missing_auth.py     # Security test: Missing Authorization header (401 expected)
├── test_invalid_auth.py     # Security test: Invalid Bearer token (401 expected)
├── test_missing_voice.py    # Negative test: Payload missing required 'voice_id'
├── test_invalid_payload.py  # Negative test: Empty 'text' string payload
│
├── test_stt.py              # Functional test: Batch STT transcription via remote URL
├── test_stt_websocket.py    # Functional & Perf test: Live streaming STT via WebSocket
└── test_stt_reconnect.py    # Resilience test: Socket interruption & clean reconnect
```

---

## ⚙️ Prerequisites & Installation

### Requirements
- **Python**: 3.9 or higher
- **Smallest AI API Key**: Obtainable from the [Smallest AI Console](https://smallest.ai).

### Setup

1. **Clone or navigate to the repository:**
   ```bash
   cd smallest-api-qa
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # On macOS/Linux:
   python3 -m venv venv
   source venv/bin/activate

   # On Windows (PowerShell):
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # On Windows (Command Prompt):
   venv\Scripts\activate.bat
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🔐 Configuration & Authentication

### Option 1: Environment File (`.env`)
You can configure your credentials and endpoint settings in a local `.env` file:
1. Copy the template:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and set your key:
   ```env
   SMALLEST_API_KEY=your_smallest_api_key_here
   ```

*(Note: `.env` is already configured in `.gitignore` to prevent leaking credentials).*

### Option 2: Interactive Prompt (`getpass`)
If no environment variable is preset, scripts prompt for your API key at runtime using `getpass.getpass()`. This ensures:
- **No hardcoded secrets** in source code or version control.
- **No plaintext exposure** in terminal history or environment inspection.

When prompted:
```text
Enter your Smallest API key: [input hidden]
```
Simply paste your key and press **Enter**.

---

## 🚀 Running the Tests

### 1. Audio Verification

Before running STT streaming tests, verify the local test fixture (`sample.wav`):

```bash
python check_audio.py
```

**Expected output:**
```text
Channels: 1
Sample rate: 24000
Sample width: 2 bytes
Frames: 134400
Duration: 5.6 seconds
```
*(Requirements for STT streaming: 1 Channel / Mono, 24,000 Hz, 16-bit / 2-byte width).*

---

### 2. Text-to-Speech (TTS) Tests

#### Baseline Synthesis (Happy Path)
Generates audio from input text and saves `tts_test.wav`:
```bash
python test_tts.py
```
- **Endpoint**: `POST https://api.smallest.ai/waves/v1/tts`
- **Output**: `tts_test.wav` created in workspace, HTTP 200, response time recorded.

#### Security: Missing Authentication
Tests API behavior when no `Authorization` header is passed:
```bash
python test_missing_auth.py
```
- **Expected Status**: `401 Unauthorized`

#### Security: Invalid Authentication
Tests API behavior when an invalid Bearer token is passed:
```bash
python test_invalid_auth.py
```
- **Expected Status**: `401 Unauthorized`

#### Validation: Missing `voice_id`
Tests API payload validation when `voice_id` is omitted:
```bash
python test_missing_voice.py
```
- **Expected Status**: `400 Bad Request` or `422 Unprocessable Entity`

#### Validation: Empty Payload Text
Tests API payload validation when `text` is an empty string (`""`):
```bash
python test_invalid_payload.py
```
- **Expected Status**: Client validation error / `400 Bad Request`

---

### 3. Speech-to-Text (STT) Tests

#### Batch REST STT (Remote URL)
Transcribes remote audio via HTTP POST:
```bash
python test_stt.py
```
- **Endpoint**: `POST https://api.smallest.ai/waves/v1/stt/?model=pulse&language=en`
- **Expected Status**: `200 OK` with JSON transcription output.

#### Live Streaming STT (WebSocket)
Streams `sample.wav` in 4KB chunks and receives real-time word transcripts:
```bash
python test_stt_websocket.py
```
- **Endpoint**: `wss://api.smallest.ai/waves/v1/stt/live?...`
- **Parameters**: `model=pulse`, `language=en`, `encoding=linear16`, `sample_rate=24000`, `word_timestamps=true`
- **Expected Output**: Connected socket, streamed frames, received transcript events, clean closure.

#### WebSocket Interruption & Reconnection Resilience
Tests resilience by abruptly dropping a connection (code `1011`) mid-stream and establishing a fresh session:
```bash
python test_stt_reconnect.py
```
- **Expected Output**: Phase 1 intentional interruption handled cleanly; Phase 2 fresh session established and full audio transcribed without corruption.

---

## 📊 Test Matrix

| Test Script | Target Endpoint | Protocol | Category | Expected Result |
|-------------|-----------------|----------|----------|-----------------|
| `check_audio.py` | Local `sample.wav` | File I/O | Prerequisite | Validates Mono, 24kHz, 16-bit PCM |
| `test_tts.py` | `/waves/v1/tts` | REST (POST) | Functional / Synthesis | `200 OK`, audio stream saved to disk |
| `test_missing_auth.py` | `/waves/v1/tts` | REST (POST) | Security / Auth | `401 Unauthorized` |
| `test_invalid_auth.py` | `/waves/v1/tts` | REST (POST) | Security / Auth | `401 Unauthorized` |
| `test_missing_voice.py` | `/waves/v1/tts` | REST (POST) | Input Validation | `400` / `422` error response |
| `test_invalid_payload.py` | `/waves/v1/tts` | REST (POST) | Input Validation | Validation error on empty text |
| `test_stt.py` | `/waves/v1/stt/` | REST (POST) | Functional / STT | `200 OK`, valid JSON transcription |
| `test_stt_websocket.py` | `/waves/v1/stt/live` | WebSocket | Streaming / Real-time | Real-time events, valid final transcript |
| `test_stt_reconnect.py` | `/waves/v1/stt/live` | WebSocket | Fault Tolerance | Clean recovery & full transcript on retry |

---

## 🛡️ Best Practices & Security

- **Credential Hygiene**: Never hardcode production API keys. Always use secure input prompts (`getpass`) or environment variables loaded from `.env` (ignored by git).
- **Latency Measurement**: Each script uses high-resolution monotonic timers (`time.perf_counter()`) to capture true end-to-end network and processing latency.
- **Traceability**: All test scripts log `x-request-id` header values for cross-referencing with backend server logs.
- **Timeouts**: Every network call sets explicit connection and read timeouts (`timeout=(10, 30)` or `timeout=(10, 60)`) to prevent hanging processes.

---

## 📄 Related Documents

- [qa-report.md](file:///d:/BACKEND-2026/smallest-api-qa/qa-report.md) — Comprehensive QA execution results, latency benchmarks, edge cases, defects, and recommendations.
