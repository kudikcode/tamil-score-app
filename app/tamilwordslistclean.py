# clean_tamil_hunspell.py
# Run this AFTER you created tamil_words.txt from Hunspell.
# It writes tamil_words_clean.txt with likely English transliterations removed.

from pathlib import Path
import unicodedata as ud

# Tamil consonants (base letters)
TAMIL_CONSONANTS = set("கஙசஞடணதநபமயரலவழளறனஜஷஸஹ")  # include Grantha set too
VIRAMA = "்"  # pulli
AYTHAM = "ஃ"

# Heuristic 1: contains clearly foreign/Grantha letters or aytham-f combos
FOREIGN_LETTERS = set("ஜஷஸஹ")  # conservative: often marks Sanskrit/English borrowings
AYTHAM_COMBOS = ("ஃப", "ஃஜ", "ஃக", "ஃத", "ஃஸ", "ஃஹ")  # used to render f, z, etc.

# Heuristic 2: clusters like ஸ்க, ஸ்ட, ஸ்ப, ஸ்ம, ஸ்ல, ஸ்வ, ஸ்ட்ர (very common in English loans)
LIKELY_CLUSTER_PREFIXES = ("ஸ்" + c for c in "கடபமலவறரநஞசதபஸஷஜஹக்ரட்ரட்லஸ்ட்ர")  # expandable
LIKELY_CLUSTER_PREFIXES = set(LIKELY_CLUSTER_PREFIXES) | {"ஸ்க", "ஸ்ட", "ஸ்ப", "ஸ்ம", "ஸ்ல", "ஸ்வ", "ஸ்ட்ர"}

# Heuristic 3: final bare consonant endings (rare in native Tamil; common in loans)
FINAL_BARE_CONSONANT = ("ஸ்", "ஷ்", "ஜ்", "ஹ்")

def has_latin_translit_cluster(word: str) -> bool:
    # Look for sequences like "ஸ்"+"<consonant>" = cluster used in loans
    for i in range(len(word) - 1):
        if word[i] == "ஸ்":
            nxt = word[i + 1]
            if nxt in TAMIL_CONSONANTS:  # consonant following bare 'ஸ்'
                return True
    # Also check explicit prefixes
    for p in LIKELY_CLUSTER_PREFIXES:
        if word.startswith(p):
            return True
    return False

def looks_like_ing_transliteration(word: str) -> bool:
    # Most "-ing" transliterations end with "ிங்" (i + ng + virama) or with a long vowel before "ங்"
    # We'll flag words that end with "ங்" and have Latin-like cluster earlier.
    if not word.endswith("ங்"):
        return False
    # If the word also contains a suspicious cluster earlier, treat as loan
    return has_latin_translit_cluster(word) or "ட்" in word or "ட்" + VIRAMA in word

def is_probable_transliteration(word: str) -> bool:
    # Normalize to NFC to be safe
    word = ud.normalize("NFC", word)

    # Reject very short tokens
    if len(word) <= 1:
        return True

    # Heuristic 1: foreign letters or aytham-based combos
    if any(ch in FOREIGN_LETTERS for ch in word):
        # Many genuine Sanskrit loans will match this; if you want to KEEP Sanskrit,
        # you can weaken this to only reject words that ALSO match other rules.
        return True
    if any(combo in word for combo in AYTHAM_COMBOS):
        return True

    # Heuristic 2: consonant-cluster patterns typical in English loans
    if has_latin_translit_cluster(word):
        return True

    # Heuristic 3: ends with bare consonant like "ஸ்"
    if word.endswith(FINAL_BARE_CONSONANT):
        return True

    # Heuristic 4: "-ing" style
    if looks_like_ing_transliteration(word):
        return True

    return False

def clean_dictionary(in_path="tamil_words.txt", out_path="tamil_words_clean.txt"):
    words = [w.strip() for w in Path(in_path).read_text(encoding="utf-8").splitlines() if w.strip()]

    kept, dropped = [], []
    for w in words:
        if is_probable_transliteration(w):
            dropped.append(w)
        else:
            kept.append(w)

    Path(out_path).write_text("\n".join(sorted(set(kept))), encoding="utf-8")
    print(f"Input:  {len(words):,}")
    print(f"Kept:   {len(set(kept)):,}")
    print(f"Dropped:{len(set(dropped)):,}  (likely transliterations)")

if __name__ == "__main__":
    clean_dictionary()
