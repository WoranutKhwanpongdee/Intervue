import io
import logging
from pypdf import PdfReader

logger = logging.getLogger("intervue.resume")


def extract_text_from_file(filename: str, file_bytes: bytes) -> str:
    """Extract clean text from uploaded resume (PDF or TXT/MD)."""
    fn_lower = filename.lower()
    
    if fn_lower.endswith(".pdf"):
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            text_parts = []
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            extracted = "\n\n".join(text_parts).strip()
            if extracted:
                return extracted
            return "No readable text found in PDF."
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            raise ValueError(f"Could not parse PDF file: {e}")

    # Plain text / markdown fallback
    try:
        return file_bytes.decode("utf-8", errors="replace").strip()
    except Exception as e:
        logger.error(f"Error decoding text: {e}")
        raise ValueError(f"Could not read text file: {e}")
