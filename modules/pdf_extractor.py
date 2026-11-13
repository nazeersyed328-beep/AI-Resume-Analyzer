"""
PDF Extractor Module
Responsible for safely extracting plain text from PDF resumes.
Handles:
- File paths and in-memory file objects (Streamlit UploadedFile)
- Multi-page resumes
- Password-protected / encrypted PDFs
- Corrupted / unreadable PDFs
- Scanned (image-only) resumes with zero extractable text
"""

import io
import os
from typing import Union, Dict, Any
import pypdf
from pypdf.errors import PdfReadError


def extract_text_from_pdf(pdf_source: Union[str, io.BytesIO, bytes]) -> Dict[str, Any]:
    """
    Extracts text from a PDF file source.

    Args:
        pdf_source: A file path (str), a BytesIO stream, or raw bytes.

    Returns:
        dict: A dictionary containing:
            - success (bool): True if text was extracted successfully
            - text (str): The concatenated text from all pages
            - num_pages (int): Total number of pages in the PDF
            - is_scanned (bool): True if the PDF has pages but no extractable text
            - error (str or None): Error message if extraction failed
    """
    # 1. Normalize input to a file-like stream or path
    if isinstance(pdf_source, str) and not os.path.exists(pdf_source):
        return {
            "success": False,
            "text": "",
            "num_pages": 0,
            "is_scanned": False,
            "error": "The specified PDF file was not found.",
        }
    if isinstance(pdf_source, bytes):
        pdf_source = io.BytesIO(pdf_source)

    try:
        # 2. Initialize the PyPDF reader
        reader = pypdf.PdfReader(pdf_source)

        # 3. Handle Encrypted / Password-Protected PDFs
        if reader.is_encrypted:
            # Try decrypting with an empty password (some PDFs have default blank encryption)
            try:
                decrypted = reader.decrypt("")
                if decrypted == 0:  # 0 indicates decryption failed
                    return {
                        "success": False,
                        "text": "",
                        "num_pages": 0,
                        "is_scanned": False,
                        "error": "The PDF is password-protected. Please provide an unprotected file."
                    }
            except Exception:
                return {
                    "success": False,
                    "text": "",
                    "num_pages": 0,
                    "is_scanned": False,
                    "error": "The PDF is password-protected and cannot be read."
                }

        num_pages = len(reader.pages)
        if num_pages == 0:
            return {
                "success": False,
                "text": "",
                "num_pages": 0,
                "is_scanned": False,
                "error": "The uploaded PDF contains no pages."
            }

        # 4. Extract text from each page
        extracted_pages = []
        for page_idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            extracted_pages.append(page_text.strip())

        full_text = "\n\n".join(extracted_pages).strip()

        # 5. Detect Scanned / Image-Only PDFs
        # If pages exist but total extracted characters are less than 20, it's likely an image or scan
        if len(full_text) < 20:
            return {
                "success": False,
                "text": "",
                "num_pages": num_pages,
                "is_scanned": True,
                "error": (
                    "This PDF appears to be a scanned image or photo. "
                    "PyPDF cannot extract text from image-only PDFs without OCR. "
                    "Please upload a text-based PDF."
                )
            }

        # 6. Extraction Successful
        return {
            "success": True,
            "text": full_text,
            "num_pages": num_pages,
            "is_scanned": False,
            "error": None
        }

    except PdfReadError:
        return {
            "success": False,
            "text": "",
            "num_pages": 0,
            "is_scanned": False,
            "error": "Corrupted or invalid PDF format. Please upload a valid, text-based PDF."
        }
    except FileNotFoundError:
        return {
            "success": False,
            "text": "",
            "num_pages": 0,
            "is_scanned": False,
            "error": "The specified PDF file could not be read."
        }
    except Exception:
        return {
            "success": False,
            "text": "",
            "num_pages": 0,
            "is_scanned": False,
            "error": "An unexpected error occurred while reading the PDF. Please try a different text-based PDF file."
        }

