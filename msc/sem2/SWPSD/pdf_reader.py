import argparse
import json
import os
from typing import Dict, List, Tuple

import pdfplumber


class PDFReader:
    """
    Handles extraction of text and basic structure from PDF files.
    """
    
    def __init__(self, pdf_path: str):
        """
        Initialize the PDF reader with a path to a PDF file.
        
        Args:
            pdf_path: Path to the PDF file to read
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        self.pdf_path = pdf_path
        
    def extract_content(self) -> List[Dict]:
        """
        Extract content from the PDF file.
        
        Returns:
            List of dictionaries containing page content with text and metadata
        """
        document_content = []
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    
                    # Extract heading information based on font sizes
                    headings = self._extract_headings(page)
                    
                    document_content.append({
                        "page_number": i + 1,
                        "text": text,
                        "headings": headings,
                        "images": len(page.images)
                    })
                    
            return document_content
            
        except Exception as e:
            raise RuntimeError(f"Error extracting content from PDF: {str(e)}")
    
    def _extract_headings(self, page) -> List[Tuple[str, float]]:
        """
        Extract potential headings from a page based on font characteristics.
        
        Args:
            page: A pdfplumber page object
            
        Returns:
            List of tuples with (text, font_size) for potential headings
        """
        headings = []
        
        # Extract text with font size information
        if page.chars:
            # Group text by font size and position
            lines = {}
            current_y = None
            current_line = []
            
            # Sort chars by y position, then x position
            chars = sorted(page.chars, key=lambda c: (c["top"], c["x0"]))
            
            for c in chars:
                if current_y is None or abs(c["top"] - current_y) > 3:  # New line
                    if current_line:
                        text = "".join(ch["text"] for ch in current_line)
                        font_size = sum(ch["size"] for ch in current_line) / len(current_line)
                        if text.strip():
                            lines[text.strip()] = font_size
                    current_y = c["top"]
                    current_line = [c]
                else:
                    current_line.append(c)
            
            # Add the last line
            if current_line:
                text = "".join(c["text"] for c in current_line)
                font_size = sum(c["size"] for c in current_line) / len(current_line)
                if text.strip():
                    lines[text.strip()] = font_size
            
            # Find average font size for this page
            if lines:
                avg_font_size = sum(lines.values()) / len(lines)
                
                # Consider text with font size larger than average as potential headings
                for text, size in lines.items():
                    if size > avg_font_size * 1.2 and len(text) < 100:
                        headings.append((text, size))
        
        return sorted(headings, key=lambda x: x[1], reverse=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract content from a PDF file")
    parser.add_argument("pdf_path", type=str, help="Path to the PDF file")
    parser.add_argument("--output", type=str, help="Path to the output file")
    args = parser.parse_args()

    reader = PDFReader(args.pdf_path)
    content = reader.extract_content()
    if args.output:
        with open(args.output, "w") as f:
            json.dump(content, f, indent=4)
    else:
        print(content)
