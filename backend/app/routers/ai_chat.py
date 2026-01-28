"""
AI Chat API router.
Handles housing codes Q&A using Claude AI.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from ..database import get_db
from ..services.ai_service import AIService


router = APIRouter()


# Pydantic schemas
class QuestionRequest(BaseModel):
    question: str
    jurisdiction: Optional[str] = None


class SourceResponse(BaseModel):
    code_section: str
    title: str
    jurisdiction: str
    source_name: str
    source_url: str
    last_updated: Optional[str]


class AnswerResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    confidence: str
    codes_found: int


class HousingCodeRequest(BaseModel):
    code_section: str
    title: str
    content: str
    jurisdiction: str
    category: Optional[str] = None
    source_name: Optional[str] = None
    source_url: Optional[str] = None


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(
    request: QuestionRequest,
    db: Session = Depends(get_db)
):
    """
    Ask a question about housing codes and regulations.

    The AI will search relevant building codes and provide an answer
    with proper citations.

    Example questions:
    - "What are the setback requirements for residential properties?"
    - "What's the minimum ceiling height for bedrooms?"
    - "Do I need a permit to build a deck?"
    """
    try:
        ai_service = AIService(db)
        result = await ai_service.answer_housing_question(
            question=request.question,
            jurisdiction=request.jurisdiction
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")


@router.post("/codes")
async def add_housing_code(
    code_request: HousingCodeRequest,
    db: Session = Depends(get_db)
):
    """
    Add a new housing code to the database.

    This endpoint is used to populate the housing codes database
    for the AI to reference.
    """
    try:
        ai_service = AIService(db)
        code = await ai_service.add_housing_code(
            code_section=code_request.code_section,
            title=code_request.title,
            content=code_request.content,
            jurisdiction=code_request.jurisdiction,
            category=code_request.category,
            source_name=code_request.source_name,
            source_url=code_request.source_url
        )

        return {
            "message": "Housing code added successfully",
            "code_section": code.code_section,
            "id": code.id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add code: {str(e)}")


@router.get("/codes/search")
async def search_codes(
    query: str,
    jurisdiction: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Search housing codes directly without AI processing.
    Useful for exploring what codes are available.
    """
    try:
        ai_service = AIService(db)
        codes = ai_service._search_housing_codes(
            query=query,
            jurisdiction=jurisdiction,
            limit=limit
        )

        return {
            "query": query,
            "count": len(codes),
            "codes": [
                {
                    "id": code.id,
                    "code_section": code.code_section,
                    "title": code.title,
                    "jurisdiction": code.jurisdiction,
                    "category": code.category,
                    "source_url": code.source_url
                }
                for code in codes
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/health")
async def ai_health_check(db: Session = Depends(get_db)):
    """Check if AI service is configured correctly."""
    try:
        ai_service = AIService(db)
        return {
            "status": "healthy",
            "model": ai_service.model,
            "api_configured": bool(ai_service.api_key)
        }
    except ValueError as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
