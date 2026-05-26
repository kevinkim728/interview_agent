# AI Interview Agent

An end-to-end AI interview system that:

- Connects the browser to OpenAI Realtime via WebRTC for a live, voice-based screening interview
- Records both sides of the conversation in the browser
- Saves the audio to the server and converts it with FFmpeg
- Transcribes with Whisper, performs speaker diarization with pyannote, then labels speakers
- Analyzes the conversation with the OpenAI API and generates a concise report

## Architecture

```
+-------------------+                 +-----------------------------+
|   Browser (UI)    |                 |      OpenAI Realtime API    |
|-------------------|   WebRTC (SDP)  |                             |
| interview_agent.  |<--------------->|  Ephemeral session + audio  |
| html + webrtc_    |                 +-----------------------------+
| client.js         |
|                   |   POST /save-interview (audio)
|  Record mixed     |-----------------------------------------+
|  user+AI audio    |                                         |
+---------^---------+                                         v
          |                                     +---------------------------+
          |                                     | FastAPI Server            |
          |   GET /session (ephemeral key)      | (`WebRTC_server.py`)      |
          +------------------------------------>| - Issues ephemeral token  |
                                                | - Saves WebM, FFmpeg->WAV |
                                                | - Whisper transcription   |
                                                | - pyannote diarization    |
                                                | - Label speakers          |
                                                | - Analyze via OpenAI API  |
                                                | - Write transcript/report |
                                                +---------------------------+
                                                               |
                                                               v
                                                interviews/interview_*.txt
```

## Setup

**1. Install system dependencies**
```bash
brew install ffmpeg
```

**2. Environment variables**

Create a `.env` file in the project root:
```
OPENAI_API_KEY=sk-...
HUGGINGFACE_TOKEN=hf_...
```

**3. Install Python dependencies**

If you don't have `uv` installed:
```bash
brew install uv
```

Then install dependencies:
```bash
uv sync
```

**4. Add the job description**

Open `job_config.py` and paste the job description into the `JOB_DESCRIPTION` variable.

> Note: The server loads Whisper and pyannote on startup — there will be a delay on first run while models download.

## Run

```bash
python WebRTC_server.py
```

Then open `http://localhost:3000` in your browser.

- Click **Start Interview** to establish the WebRTC session
- Speak with the AI interviewer
- Click **End Interview** to stop recording and upload audio
- The server will transcribe, diarize, analyze, and write outputs to `interviews/`

## Output

- `interview_<timestamp>_labeled.txt` — speaker-labeled transcript (INTERVIEWER / CANDIDATE)
- `interview_<timestamp>_report.txt` — structured analysis with scores, highlights, concerns, and a hiring recommendation


## Configuration

- **Realtime model:** set via `MODEL` in `WebRTC_server.py`
- **Analysis model:** set via `model` in `interview_analyzer.py` (default `gpt-4o-mini`)
- **Whisper model:** `base` by default — change in `WebRTC_server.py` if needed
- **Job description:** paste into `job_config.py` under `JOB_DESCRIPTION` before running
- **Interview prompt:** customize in `WebRTC_server.py` under `INTERVIEW_PROMPT`
- **Analysis prompt:** customize in `interview_analyzer.py` under `ANALYZER_PROMPT`

## Troubleshooting

- **FFmpeg not found** — install via `brew install ffmpeg`
- **pyannote auth error** — check your `HUGGINGFACE_TOKEN` and confirm you accepted the model terms on Hugging Face
- **401 from OpenAI** — check your `OPENAI_API_KEY` and confirm `/session` is reachable
- **No files in `interviews/`** — confirm you clicked **End Interview** so the browser uploads the recording
- **Slow processing** — use a machine with a GPU; reduce Whisper model size if needed

## Tech Stack

- **FastAPI** — server and post-processing pipeline
- **OpenAI Realtime API** — live voice interview over WebRTC
- **Whisper** — audio transcription
- **pyannote** — speaker diarization
- **OpenAI structured output** — interview analysis
