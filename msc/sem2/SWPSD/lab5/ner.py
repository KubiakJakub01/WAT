import spacy

# Load pre-trained model (e.g., for English)
nlp = spacy.load("en_core_web_sm")


def detect_entities(text):
    doc = nlp(text)

    entities = {
        "PERSON": [],
        "ORG": [],
        "GPE": [],  # Geopolitical Entity (countries, cities, states)
        "LOC": [],  # Locations (mountains, rivers, etc.)
    }

    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)

    return entities


if __name__ == "__main__":
    text = "Apple is looking at buying U.K. startup for $1 billion. Steve Jobs founded Apple in Cupertino."
    results = detect_entities(text)

    print("Osoby:", results["PERSON"])
    print("Organizacje:", results["ORG"])
    print("Lokalizacje (GPE):", results["GPE"])
    print("Lokalizacje (LOC):", results["LOC"])
