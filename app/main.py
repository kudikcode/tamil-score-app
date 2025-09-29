\
import os
import re
import tempfile
from typing import Dict, Any

from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Sarvam AI SDK
from sarvamai import SarvamAI

#util
from fuzzy_tamil_util import FuzzyTamilMatcher

matcher = FuzzyTamilMatcher("tamil_words_pure.txt")
API_KEY = os.getenv("SARVAM_API_KEY") or os.getenv("SARVAMAI_API_KEY") or os.getenv("SARVAM_API_SUBSCRIPTION_KEY")

print("*******")
print(API_KEY)

if not API_KEY:
    # We don't crash on startup; we'll error on first call with a clear message.
    pass

app = FastAPI(title="Tamil-English Score App (Sarvam AI)")

# Static & templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def count_words_and_score(text: str) -> Dict[str, Any]:
    """
    Count total words and English words in a Unicode-safe way.
    - Total words: tokens that contain at least one alphabetic character in any script.
    - English words: tokens containing only ASCII letters A-Z/a-z.
    """
    # Tokenize: split on whitespace and punctuation, keep letters/numbers in tokens
    #tokens = re.findall(r"\b[\w'-]+\b", text, flags=re.UNICODE)
    tokens = text.split()
    print(tokens)

    def is_word(tok: str) -> bool:
        return any(ch.isalpha() for ch in tok)

    def is_english(tok: str) -> bool:
        return re.fullmatch(r"[A-Za-z]+(?:'[A-Za-z]+)?", tok) is not None
    
    def is_tamil(tok: str) -> bool:
        return matcher.is_tamil(tok, 0.92)
    
    def bucket_tokens(tokens):
        """
        Split tokens into Tamil and English buckets in one pass.
        Returns: (english_words_count, english_words, tamil_words)
        TODO: Need to finetune the approach
        """
        english_words = []
        tamil_words = []

        for t in tokens:
            if is_tamil(t):
                tamil_words.append(t)
            else:
                english_words.append(t)

        return len(english_words), english_words, tamil_words

    total_words_count = sum(1 for t in tokens if is_word(t))
    english_words_count, english_words, tamil_words = bucket_tokens(tokens)

    print("English count:", english_words_count)
    print("English words:", english_words)
    print("Tamil words:", tamil_words)

    score = None
    score_str = None
    if english_words_count > 0:
        score = total_words_count / english_words_count
        score_str = f"{score:.3f}"
    else:
        score = total_words_count
        score_str = f"{score:.3f}"
        print("(no English words) spoken...")
    return {
        "total_words_count": total_words_count,
        "english_words_count": english_words_count,
        "tamil_words": tamil_words,
        "english_words": english_words,
        "score": score,
        "score_display": score_str,
    }


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    if API_KEY is None:
        raise HTTPException(status_code=500, detail="Missing API key. Set SARVAM_API_KEY environment variable.")

    # Save upload to a temp file for SDK
    try:
        suffix = os.path.splitext(audio.filename or "")[1] or ".webm"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await audio.read()
            tmp.write(content)
            tmp_path = tmp.name
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read audio: {e}")

    try:
        client = SarvamAI(api_subscription_key=API_KEY)
        # SDK accepts file-like or path. We'll open as binary.
        with open(tmp_path, "rb") as f:
            # Let model auto-detect language (Tamil or code-mixed)
            resp = client.speech_to_text.transcribe(file=f)
        transcript = resp.get("transcript") if isinstance(resp, dict) else getattr(resp, "transcript", None)
        language_code = resp.get("language_code") if isinstance(resp, dict) else getattr(resp, "language_code", None)
        if not transcript:
            raise RuntimeError("No transcript returned from Sarvam API")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Transcription failed: {e}")
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    metrics = count_words_and_score(transcript)

    return JSONResponse(
        {
            "transcript": transcript,
            "language_code": language_code,
            **metrics,
        }
    )


# Health endpoint
@app.get("/healthz")
async def healthz():
    return {"ok": True}
