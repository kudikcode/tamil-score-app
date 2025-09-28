#pip install open-tamil fuzzywuzzy python-Levenshtein
from pathlib import Path
from fuzzywuzzy import process, fuzz


class FuzzyTamilMatcher:
    """
    Utility class for Tamil fuzzy matching.
    Loads the dictionary once and exposes a simple API for scoring words.
    """

    def __init__(self, dict_path: str = "tamil_words_pure.txt"):
        if not Path(dict_path).exists():
            raise FileNotFoundError(f"Tamil dictionary not found: {dict_path}")
        self.dict_words = self._load_dictionary(dict_path)

    @staticmethod
    def _load_dictionary(path: str):
        """Load dictionary words from file into memory."""
        with open(path, "r", encoding="utf-8") as f:
            return [w.strip() for w in f if w.strip()]

    def get_score(self, word: str, top_n: int = 1):
        """
        Return the top-N closest matches for the given Tamil word.
        Returns list of (match_word, score) where score ∈ [0.0, 1.0].
        """
        matches = process.extract(word, self.dict_words, scorer=fuzz.ratio, limit=top_n)
        return [(m, s / 100.0) for m, s in matches]

    def is_tamil(self, tok: str, expected_score: float) -> bool:
        result = self.get_score(tok, top_n=3)
        if result:
            _, score = result[0]
            print("tok: " + tok)
            print(score)
            return score >= expected_score  
        return False

# Example usage (for testing only)
if __name__ == "__main__":
    matcher = FuzzyTamilMatcher("tamil_words_pure.txt")

    test_words = [
        "அமா", "விடு", "மரம", "நாயி",
        "ஸ்கூல்", "பண்ணுகிறேன்", "ஸ்கேட்டிங்", "டிரெயினிங்"
    ]

    for tw in test_words:
        results = matcher.get_score(tw, top_n=3)
        print(f"{tw} → {results}")
