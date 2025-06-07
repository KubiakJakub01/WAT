import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('stopwords')
nltk.download('punkt')

def remove_stopwords_nltk(text, language='english'):
    # Get stop words list for given language
    stop_words = set(stopwords.words(language))
    
    # Text tokenization
    words = word_tokenize(text)
    
    # Filter stop words
    filtered_words = [word for word in words if word.lower() not in stop_words]
    
    return ' '.join(filtered_words)

if __name__ == "__main__":

    # Example usage for English
    text_en = "This is a sample, sentence showing off stop words filtration."
    filtered_en = remove_stopwords_nltk(text_en, 'english')
    print("Without stopwords (NLTK EN):", filtered_en)
