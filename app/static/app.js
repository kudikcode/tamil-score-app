
let mediaRecorder;
let chunks = [];

const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const statusEl = document.getElementById('status');

const resultsSection = document.getElementById('results');
const transcriptEl = document.getElementById('transcript');
const langEl = document.getElementById('language');
const totalWordsCountEl = document.getElementById('totalWordsCount');
const englishWordsCountEl = document.getElementById('englishWordsCount');
const tamilWordsEl = document.getElementById('tamilWords');
const englishWordsEl = document.getElementById('englishWords');
const scoreEl = document.getElementById('score');

async function initMedia() {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
  mediaRecorder.ondataavailable = e => { if (e.data.size > 0) chunks.push(e.data); };
  mediaRecorder.onstart = () => { chunks = []; statusEl.textContent = "Recording... speak now"; };
  mediaRecorder.onstop = onStop;
}

async function onStop() {
  statusEl.textContent = "Processing...";
  const blob = new Blob(chunks, { type: 'audio/webm' });
  const form = new FormData();
  form.append('audio', blob, 'input.webm');
  try {
    const resp = await fetch('/api/transcribe', { method: 'POST', body: form });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      throw new Error(err.detail || ('HTTP ' + resp.status));
    }
    const data = await resp.json();
    transcriptEl.textContent = data.transcript || '';
    langEl.textContent = data.language_code || 'unknown';
    totalWordsCountEl.textContent = data.total_words_count;
    englishWordsCountEl.textContent = data.english_words_count;
    tamilWordsEl.textContent = data.tamil_words
    englishWordsEl.textContent = data.english_words
    scoreEl.textContent = data.score_display;

    resultsSection.classList.remove('hidden');
    statusEl.textContent = "Done";
  } catch (e) {
    statusEl.textContent = "Error: " + e.message;
    console.error(e);
  } finally {
    startBtn.disabled = false;
    stopBtn.disabled = true;
  }
}

startBtn.addEventListener('click', async () => {
  startBtn.disabled = true;
  stopBtn.disabled = false;
  if (!mediaRecorder) await initMedia();
  mediaRecorder.start();
});

stopBtn.addEventListener('click', () => {
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.stop();
  }
});
