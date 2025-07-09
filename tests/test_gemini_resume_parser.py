from pathlib import Path
import sys
import os
import fitz  # PyMuPDF

# Optional: Add root if needed
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from backend.gemini_resume_parser import parse_resume_with_gemini

def extract_text_from_pdf_pymupdf(pdf_path):
    """Extracts text from a PDF using PyMuPDF (fitz)"""
    doc = fitz.open(pdf_path)
    extracted_text = ""
    for page in doc:
        extracted_text += page.get_text() + "\n"
    doc.close()
    return extracted_text

# rovide your resume file path
pdf_file = "C:/Users/vemur/OneDrive/Desktop/Resumes/NewResume/Chewy/MohanRam-Resume.pdf"

if not os.path.exists(pdf_file):
    print(f"File not found: {pdf_file}")
    sys.exit(1)

# Extract text and parse with Gemini
text_content = extract_text_from_pdf_pymupdf(pdf_file)
result = parse_resume_with_gemini(text_content)

#  Output
print(result)
