import logging
from io import BytesIO
import pymupdf
from ai_engine.ingestion.ocr import extract_text_from_image

logger = logging.getLogger(__name__)

def extract_pdf_pages(content:bytes) -> list[dict]:
    """
    Extract text from every PDF page.
    Returns:
        [
            {
                "page": 1,
                "text": "...",
                "source": "TEXT"
            },
            {
                "page": 2,
                "text": "...",
                "source": "OCR"
            }
        ]
    """
    if not content:
        raise ValueError("Empty PDF content provided.")
    
    pages = []
    try:
        pdf_document = pymupdf.open(
            stream=BytesIO(content),
            filetype="pdf"
        )
        
        if pdf_document.is_encrypted:
            raise ValueError("Encrypted PDF files are not supported.")
        if pdf_document.page_count == 0:
            raise ValueError("The PDF file contains no pages.")
        
        for page_index in range(pdf_document.page_count):
            page = pdf_document.load_page(page_index)
            extracted_text = page.get_text("text")
            # Use OCR when the embedded text is missing or insufficient.
            if len(extracted_text) < 20:
                pixmap = page.get_pixmap(
                        matrix=pymupdf.Matrix(2, 2),
                        alpha=False
                    )
                image_bytes = pixmap.tobytes("png")
                extracted_text = extract_text_from_image(image_bytes)
                source = "OCR"
            else:
                source = "TEXT"
            pages.append({
                "page": page_index + 1,
                "text": extracted_text,
                "source": source
            })
            
        pdf_document.close()
        return pages
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise ValueError("Failed to extract text from the PDF file.")
            
            