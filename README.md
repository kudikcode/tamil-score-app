# Tamil–English Score App (Sarvam AI)

A tiny FastAPI web app that:
1) listens to your microphone in the browser,
2) uses **Sarvam AI** Speech-to-Text to transcribe Tamil / code-mixed speech,
3) counts **English words** in the transcript,
4) computes `score = total_words_count / english_words_count`,
5) shows everything in a simple UI.

> ⚠️ If there are no English words, the score is shown as `∞ (no English words)`.

---

## Quick Start

```bash
# 1) Create & activate a virtual env (recommended)
python3 -m venv .venv && source .venv/bin/activate

# 2) Install deps
pip install -r requirements.txt

# 3) Set your Sarvam API key
export SARVAM_API_KEY="YOUR_SARVAM_KEY"

# 4) Run
cd app
uvicorn main:app --reload --port 8000

# 5) Open the app
open http://localhost:8000
```

> You can also use `SARVAMAI_API_KEY` or `SARVAM_API_SUBSCRIPTION_KEY` env var names.

### Notes
- Uses the Sarvam **Saarika** STT model via the official Python SDK (`sarvamai`).
- Auto language-detect is used; you can force Tamil by setting `language_code="ta-IN"` in the SDK call.
- The browser records audio as **WebM/Opus** (`MediaRecorder`), which Sarvam's API supports.

## How We Count Words
- **Total words:** tokens that contain at least one letter in any script (Tamil, English, etc.).
- **English words:** tokens made only of ASCII letters `[A-Za-z]` (simple & robust for code-mixed Tamil-English).

## File Layout

```
tamil-english-score-app/
├─ main.py              # FastAPI app
├─ requirements.txt
├─ templates/
│  └─ index.html        # Simple UI
└─ static/
   ├─ app.js            # Browser recording & POST
   └─ style.css
```

## Production Tips
- Add CORS rules if hosting behind a different domain.
- Set `uvicorn --host 0.0.0.0 --port 8080` in containers.
- Consider Sarvam **Batch API** for >30s audio and diarization (speaker turns).

## License
MIT
