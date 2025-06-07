from spellchecker import SpellChecker

def correct_spelling_en(text):
    spell = SpellChecker(language='en')
    
    words = text.split()
    corrected_words = []
    
    for word in words:
        # Find most probable correction
        corrected_word = spell.correction(word)
        corrected_words.append(corrected_word if corrected_word is not None else word)
    
    return ' '.join(corrected_words)

# Example usage
text_en = "Ths is an exmple of misspelled Englsh text."
corrected_text = correct_spelling_en(text_en)
print(f"Original: {text_en}")
print(f"Corrected: {corrected_text}")
