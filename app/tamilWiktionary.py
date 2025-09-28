# build_tamil_words_from_wiktionary.py (auto-download wrapper)
import os, sys, bz2, re, unicodedata as ud, xml.etree.ElementTree as ET
from pathlib import Path
from urllib.request import urlopen

DUMP_URL = "https://dumps.wikimedia.org/tawiktionary/latest/tawiktionary-latest-pages-articles.xml.bz2"

def nfc(s): return ud.normalize("NFC", s)
def is_tamil_word(s):
    s = nfc(s).strip()
    return bool(s) and not re.search(r"[A-Za-z0-9]", s) and any(0x0B80<=ord(ch)<=0x0BFF for ch in s)

def extract_tamil_section(text):
    parts = re.split(r"(?m)^==\s*([^=]+)\s*==\s*$", text or "")
    for i in range(1, len(parts), 2):
        if parts[i].strip().lower() in ("tamil","ta"):
            return parts[i+1]
    return None

LEMMA_CATS = re.compile(r"\[\[\s*Category\s*:\s*Tamil\s+lemmas\s*\]\]|\{\{\s*ta-(?:noun|verb|adj|adv)\b", re.I)
EN_BORROW_RE = re.compile(r"\[\[\s*Category\s*:\s*Tamil\s+terms\s+(?:borrowed|derived)\s+from\s+English\s*\]\]|\{\{\s*(?:bor|der|inh)\s*\|\s*ta\s*\|\s*en\b", re.I)
EN_MISC_EXCLUDE = re.compile(r"English\s*loan|from\s+English|English-origin", re.I)

def page_iter(path):
    with bz2.open(path, "rb") as f:
        for ev, elem in ET.iterparse(f, events=("end",)):
            if elem.tag.endswith("page"):
                yield elem
                elem.clear()

def get_text(page):
    title = page.findtext("./{*}title") or ""
    rev = page.find("./{*}revision")
    text = rev.findtext("./{*}text") if rev is not None else ""
    return title, text or ""

def build_lexicon(dump_path, out_path):
    out = set()
    for page in page_iter(dump_path):
        title, wikitext = get_text(page)
        if not is_tamil_word(title):
            continue
        ta = extract_tamil_section(wikitext)
        if not ta: continue
        if not LEMMA_CATS.search(ta) and not re.search(r"\{\{\s*ta-(?:noun|verb|adj|adv)\b", ta, re.I):
            continue
        if EN_BORROW_RE.search(ta) or EN_MISC_EXCLUDE.search(ta):
            continue
        out.add(nfc(title))
    words = sorted(out)
    Path(out_path).write_text("\n".join(words), encoding="utf-8")
    print(f"Kept {len(words):,} Tamil lemmas (English loans excluded). Wrote: {out_path}")

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        dump, out = sys.argv[1], sys.argv[2]
    else:
        Path("data").mkdir(exist_ok=True)
        dump = "data/tawiktionary-latest-pages-articles.xml.bz2"
        if not Path(dump).exists():
            print("Downloading Tamil Wiktionary dump …")
            with urlopen(DUMP_URL) as r: Path(dump).write_bytes(r.read())
        out = "tamil_words_pure.txt"
    build_lexicon(dump, out)
