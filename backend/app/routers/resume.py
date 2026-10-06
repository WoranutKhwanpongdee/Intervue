import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.interview import ResumeParseResponse
from app.services.resume_parser import extract_text_from_file

logger = logging.getLogger("intervue.routers.resume")
router = APIRouter(prefix="/resume", tags=["Resume"])


@router.post("/parse", response_model=ResumeParseResponse)
async def parse_resume(file: UploadFile = File(...)):
    """Parse an uploaded PDF or TXT resume to extract plain text for personalization."""
    filename = file.filename or "resume.pdf"
    if not (filename.lower().endswith(".pdf") or filename.lower().endswith(".txt") or filename.lower().endswith(".md")):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload a PDF (.pdf) or text (.txt) file."
        )

    try:
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit.")

        text = extract_text_from_file(filename, content)
        return ResumeParseResponse(
            filename=filename,
            extracted_text=text,
            char_count=len(text)
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error parsing resume: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process resume: {str(e)}")
