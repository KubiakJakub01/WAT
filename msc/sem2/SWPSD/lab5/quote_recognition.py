import re

def extract_quotes_with_authors(text):
    # Pattern for quotes with quotation marks and authors
    pattern = r'(["\'])(.*?)\1(?:\s*[-–—]\s*|\s+)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
    matches = re.findall(pattern, text)
    
    quotes = []
    for match in matches:
        quotes.append({
            'quote': match[1],
            'author': match[2]
        })
    
    return quotes

# Example usage
text = """
"Pomyśl o przyszłości" - Jan Kowalski
'Marzenia są jak gwiazdy' — Maria Nowak
„Nie ma tego złego" – Adam Mickiewicz
"""

quotes = extract_quotes_with_authors(text)
for q in quotes:
    print(f"'{q['quote']}' — {q['author']}")
