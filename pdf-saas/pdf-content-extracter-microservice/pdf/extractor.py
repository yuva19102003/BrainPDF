import fitz  # PyMuPDF
import os
from typing import Dict

class PDFExtractor:
    # Intialize the PyMuPDF and Upload the PDF
    def __init__(self, pdf_path: str):
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file '{pdf_path}' not found.")
        self.pdf_path = pdf_path
        self.pdf_document = fitz.open(pdf_path)
        self.total_pages = len(self.pdf_document)

    # Extract the Content from the PDF
    def extract_content(self, start_page: int, end_page: int) -> Dict[str, str]:
        """Extract content from the given page range"""
        if start_page < 1 or end_page > self.total_pages or start_page > end_page:
            raise ValueError(f"Invalid page range! PDF has {self.total_pages} pages.")

        extracted_content = []
        for page_num in range(start_page - 1, end_page):
            page = self.pdf_document[page_num]
            text = page.get_text()
            extracted_content.append(text.strip())

        content = "\n".join(extracted_content)
        return {"content": content}
