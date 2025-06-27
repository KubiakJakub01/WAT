import string

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

nltk.download("stopwords")
nltk.download("punkt")
nltk.download("punkt_tab")


def preprocess_text(text):
    # Tokenization and removing stopwords and punctuation
    tokens = word_tokenize(text.lower())
    tokens = [
        word
        for word in tokens
        if word not in stopwords.words("english") and word not in string.punctuation
    ]
    return " ".join(tokens)


def extract_keywords_tfidf(text, n=10):
    # Text preprocessing
    processed_text = preprocess_text(text)

    # Initialize TF-IDF
    tfidf = TfidfVectorizer(ngram_range=(1, 2))  # includes bigrams too

    # Calculate TF-IDF values
    tfidf_matrix = tfidf.fit_transform([processed_text])

    # Get feature names (words/ngrams)
    feature_names = tfidf.get_feature_names_out()

    # Sort words by importance
    sorted_indices = tfidf_matrix.toarray().argsort()[0][-n:][::-1]
    keywords = [feature_names[i] for i in sorted_indices]

    return keywords


# Example usage
document = """
Python is an interpreted, high-level and general-purpose programming language.
Python's design philosophy emphasizes code readability with its notable use of significant whitespace.
Its language constructs and object-oriented approach aim to help programmers write clear,
logical code for small and large-scale projects.
"""

keywords = extract_keywords_tfidf(document)
print("Kluczowe słowa:", keywords)
