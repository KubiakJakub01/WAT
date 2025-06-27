import spacy

nlp_en = spacy.load("en_core_web_sm")


def lemmatize_en(text):
    doc = nlp_en(text)
    return [token.lemma_ for token in doc]


if __name__ == "__main__":
    text_en = "I was running quickly with the dogs that barked loudly."
    lemmas = lemmatize_en(text_en)
    print("Lemmatization (spaCy):", lemmas)
