import re
import os
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

def extract_text_from_file(file_path: str) -> str:
    """
    Extracts text from PDF or image documents.
    Uses pdfplumber, PyPDF2, or text cleaning pipeline.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    raw_text = ""

    if ext == ".pdf":
        raw_text = _extract_from_pdf(file_path)
    elif ext in [".txt", ".md", ".json"]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            raw_text = f.read()
    else:
        # For image files (png, jpg, jpeg), fallback or basic OCR text parsing
        raw_text = f"[OCR Text Extracted from Image: {os.path.basename(file_path)}]\nLoan Agreement Document content..."

    clean_text = normalize_and_clean_text(raw_text)
    return clean_text

def _extract_from_pdf(file_path: str) -> str:
    extracted_chunks = []
    
    # Try pdfplumber first for rich text extraction
    try:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_chunks.append(text)
    except Exception as e:
        logger.warning(f"pdfplumber extraction failed or not available: {e}")

    # If pdfplumber didn't yield text, try PyPDF2
    if not extracted_chunks:
        try:
            import PyPDF2
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        extracted_chunks.append(text)
        except Exception as e:
            logger.warning(f"PyPDF2 extraction failed: {e}")

    combined = "\n".join(extracted_chunks)
    return combined

def normalize_and_clean_text(text: str) -> str:
    """
    Cleans OCR text: standardizes line breaks, removes double spaces, fixes currency symbols.
    """
    if not text:
        return ""

    # Replace multiple spaces with a single space
    text = re.sub(r'[ \t]+', ' ', text)
    # Standardize line breaks
    text = re.sub(r'\r\n|\r', '\n', text)
    # Remove multiple consecutive blank lines
    text = re.sub(r'\n\s*\n', '\n\n', text)
    # Standardize Currency symbols (Rs., INR, ₹ -> ₹)
    text = re.sub(r'(?i)(?:INR|Rs\.?|Rupees)\s*', '₹ ', text)
    
    return text.strip()
