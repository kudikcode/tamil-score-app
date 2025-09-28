# some_other_module.py
from fuzzy_tamil_util import FuzzyTamilMatcher

matcher = FuzzyTamilMatcher("tamil_words_pure.txt")

word = "அமா"
best_match = matcher.get_score(word, top_n=1)
print(best_match)  # e.g., [('அம்மா', 0.92)]

for tw in ["அமா", "விடு", "மரம", "நாயி", "ஸ்கூல்", "பண்ணுகிறேன்", "ஸ்கேட்டிங்", "டிரெயினிங்"]:
    best_match = matcher.get_score(tw, top_n=1)
    print(best_match)  # e.g., [('அம்மா', 0.92)]

