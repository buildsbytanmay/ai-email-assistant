from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.database import database, models
from app.services import claude_service

router = APIRouter(prefix="/api")

class AnalyzeRequest(BaseModel):
    subject: str
    content: str

class AnalysisResponse(BaseModel):
    id: int
    subject: str
    category: str
    confidence: float
    summary: str
    generated_reply: str
    is_demo: bool = False

@router.post("/analyze", response_model=AnalysisResponse)
def analyze_email(req: AnalyzeRequest, db: Session = Depends(database.get_db)):
    if not req.subject.strip() or not req.content.strip():
        raise HTTPException(status_code=400, detail="Subject and content cannot be empty")
        
    if len(req.subject) > 500 or len(req.content) > 10000:
        raise HTTPException(status_code=400, detail="Input too long")
        
    try:
        result = claude_service.analyze_email(req.subject, req.content)
        
        db_analysis = models.EmailAnalysis(
            subject=req.subject,
            email_content=req.content,
            category=result.get("category", "Work"),
            confidence=result.get("confidence", 0.0),
            summary=result.get("summary", ""),
            generated_reply=result.get("generated_reply", "")
        )
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        
        return {
            "id": db_analysis.id,
            "subject": db_analysis.subject,
            "category": db_analysis.category,
            "confidence": db_analysis.confidence,
            "summary": db_analysis.summary,
            "generated_reply": db_analysis.generated_reply,
            "is_demo": result.get("is_demo", False)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
def get_history(db: Session = Depends(database.get_db)):
    analyses = db.query(models.EmailAnalysis).order_by(models.EmailAnalysis.created_at.desc()).all()
    return analyses

@router.delete("/history/{id}")
def delete_history(id: int, db: Session = Depends(database.get_db)):
    analysis = db.query(models.EmailAnalysis).filter(models.EmailAnalysis.id == id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    db.delete(analysis)
    db.commit()
    return {"status": "deleted"}
