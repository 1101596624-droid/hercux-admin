"""
Enhanced AI Tutor API with Learning Integration

Adds learning capabilities to existing AI tutor endpoints.
Backward compatible with existing API.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.ai_tutor import AITutorService

router = APIRouter(tags=["AI Tutor Enhanced"])


class EnhancedChatRequest(BaseModel):
    """Enhanced chat request with learning context"""
    node_id: int
    message: str
    conversation_history: List[Dict[str, str]] = []
    subject: str
    topic: str
    node_title: Optional[str] = None
    learning_objectives: Optional[List[str]] = None


class EnhancedChatResponse(BaseModel):
    """Enhanced chat response"""
    message: str
    learning_enhanced: bool = False
    template_count: int = 0


class DialogueEvaluationRequest(BaseModel):
    """Request to evaluate a dialogue session"""
    node_id: int
    dialogue: List[Dict[str, str]]
    subject: str
    topic: str


class DialogueEvaluationResponse(BaseModel):
    """Dialogue evaluation response"""
    quality_score: float
    score_breakdown: Dict[str, float]
    saved_as_template: bool
    issues: List[str]
    report: str


class LearningInsightsRequest(BaseModel):
    """Request for learning insights"""
    subject: str
    topic: str


class LearningInsightsResponse(BaseModel):
    """Learning insights response"""
    template_count: int
    avg_quality: float
    common_patterns: List[str]
    best_practices: List[str]
    quality_indicators: List[str]


class WelcomeMessageRequest(BaseModel):
    """Request for welcome message"""
    node_id: int
    node_title: str
    learning_objectives: Optional[List[str]] = None
    subject: str
    topic: str


@router.post("/chat-enhanced", response_model=EnhancedChatResponse)
async def chat_enhanced(
    request: EnhancedChatRequest,
    db: Session = Depends(get_db),
):
    """
    Enhanced chat endpoint with learning integration
    """
    try:
        tutor_service = AITutorService(db)

        node_info = {
            "id": request.node_id,
            "title": request.node_title or "this topic",
            "learning_objectives": request.learning_objectives or [],
        }

        insights = await tutor_service.get_learning_insights(
            subject=request.subject,
            topic=request.topic,
        )

        response_text = await tutor_service.generate_enhanced_response(
            user_message=request.message,
            conversation_history=request.conversation_history,
            node_info=node_info,
            subject=request.subject,
            topic=request.topic,
        )

        return EnhancedChatResponse(
            message=response_text,
            learning_enhanced=(insights["template_count"] > 0),
            template_count=insights["template_count"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate enhanced response: {str(e)}",
        )


@router.post("/evaluate-dialogue", response_model=DialogueEvaluationResponse)
async def evaluate_dialogue(
    request: DialogueEvaluationRequest,
    db: Session = Depends(get_db),
):
    """
    Evaluate a completed dialogue session
    """
    try:
        tutor_service = AITutorService(db)

        result = await tutor_service.evaluate_dialogue_session(
            dialogue=request.dialogue,
            subject=request.subject,
            topic=request.topic,
            node_id=request.node_id,
        )

        return DialogueEvaluationResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to evaluate dialogue: {str(e)}",
        )


@router.post("/learning-insights", response_model=LearningInsightsResponse)
async def get_learning_insights(
    request: LearningInsightsRequest,
    db: Session = Depends(get_db),
):
    """
    Get learning insights for a specific topic
    """
    try:
        tutor_service = AITutorService(db)

        insights = await tutor_service.get_learning_insights(
            subject=request.subject,
            topic=request.topic,
        )

        return LearningInsightsResponse(**insights)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get learning insights: {str(e)}",
        )


@router.post("/welcome-enhanced")
async def get_enhanced_welcome_message(
    request: WelcomeMessageRequest,
    db: Session = Depends(get_db),
):
    """
    Generate enhanced welcome message with learning context
    """
    try:
        tutor_service = AITutorService(db)

        node_info = {
            "id": request.node_id,
            "title": request.node_title,
            "learning_objectives": request.learning_objectives or [],
        }

        welcome_message = await tutor_service.generate_welcome_message(
            node_info=node_info,
            subject=request.subject,
            topic=request.topic,
        )

        return {"message": welcome_message}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate welcome message: {str(e)}",
        )
