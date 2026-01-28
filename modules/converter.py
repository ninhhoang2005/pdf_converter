import os
from pdfminer.high_level import extract_text
from pdf2docx import Converter
import fitz # PyMuPDF

class ConverterLogic:
    def __init__(self):
        pass

    def convert_to_txt(self, pdf_path, output_path):
        text = extract_text(pdf_path)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)

    def convert_to_html(self, pdf_path, output_path):
        # Using PyMuPDF to export to HTML
        doc = fitz.open(pdf_path)
        
        # Simple HTML structure
        html_content = "<html><body>"
        for page in doc:
            html_content += page.get_text("html")
        html_content += "</body></html>"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        doc.close()

    def convert_to_docx(self, pdf_path, output_path):
        cv = Converter(pdf_path)
        cv.convert(output_path, start=0, end=None)
        cv.close()
