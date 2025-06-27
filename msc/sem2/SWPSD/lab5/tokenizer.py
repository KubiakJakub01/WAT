import nltk
from nltk.tokenize import word_tokenize

nltk.download("punkt")  # download tokenizer resources (run once)


def tokenize_with_nltk(text):
    return word_tokenize(text)


if __name__ == "__main__":
    text = "NLP to fascynująca dziedzina! Czy zgadzasz się z tym?"
    tokens = tokenize_with_nltk(text)
    print("Tokeny (NLTK):", tokens)
