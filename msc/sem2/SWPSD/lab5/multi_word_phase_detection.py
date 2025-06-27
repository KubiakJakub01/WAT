import nltk
from nltk.collocations import BigramAssocMeasures, BigramCollocationFinder
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

nltk.download("punkt")
nltk.download("stopwords")


def find_collocations_nltk(text, top_n=20):
    # Tokenization and filtering stopwords
    tokens = [
        word.lower()
        for word in word_tokenize(text)
        if word.isalpha() and word.lower() not in stopwords.words("english")
    ]

    # Initialize bigram finder
    bigram_measures = BigramAssocMeasures()
    finder = BigramCollocationFinder.from_words(tokens)

    # Filter bigrams occurring at least 3 times
    finder.apply_freq_filter(1)

    # Return best collocations according to PMI
    return finder.nbest(bigram_measures.pmi, top_n)


# Example usage
text = """
Sztuczna inteligencja i uczenie maszynowe to dziedziny informatyki, które rozwijają się bardzo szybko.
Czarna dziura to obiekt astronomiczny o silnym polu grawitacyjnym.
Nowoczesne technologie zmieniają świat.
Systemy oparte na sztucznej inteligencji znajdują zastosowanie w wielu dziedzinach.
"""

collocations = find_collocations_nltk(text)
print("Kolokacje (NLTK PMI):")
for colloc in collocations:
    print(" ".join(colloc))
