import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.schemas.interview import ResumeParseResponse
from app.schemas.llm import ResumeAnalysis
from app.services.resume_parser import extract_text_from_file
from app.services.llm.factory import get_llm_provider

logger = logging.getLogger("intervue.routers.resume")
router = APIRouter(prefix="/resume", tags=["Resume"])


class TextAnalyzeRequest(BaseModel):
    text: str


@router.post("/parse", response_model=ResumeParseResponse)
async def parse_resume(file: UploadFile = File(...)):
    """Parse an uploaded PDF or TXT resume and extract structured skills, projects, and experiences."""
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
        
        # Analyze resume with LLM Provider
        analysis = None
        try:
            provider = get_llm_provider()
            analysis = await provider.analyze_resume(text)
        except Exception as ae:
            logger.warning(f"Could not perform structured analysis on resume: {ae}")

        return ResumeParseResponse(
            filename=filename,
            extracted_text=text,
            char_count=len(text),
            analysis=analysis
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error parsing resume: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process resume: {str(e)}")


@router.post("/analyze-text", response_model=ResumeAnalysis)
async def analyze_resume_text(req: TextAnalyzeRequest):
    """Analyze plain-text resume to extract skills, projects, and experiences."""
    if len(req.text.strip()) < 20:
        raise HTTPException(status_code=400, detail="Resume text is too short to analyze.")
    
    try:
        provider = get_llm_provider()
        return await provider.analyze_resume(req.text)
    except Exception as e:
        logger.error(f"Error analyzing text resume: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to analyze text: {str(e)}")
