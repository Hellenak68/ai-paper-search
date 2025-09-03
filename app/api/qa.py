from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User
from app.models.project import Project
from app.api.users import get_current_user
from app.services.rag_pipeline import rag_pipeline

router = APIRouter()


class QuestionRequest(BaseModel):
    question: str
    project_id: int


class QuestionResponse(BaseModel):
    answer: str
    sources: List[dict]
    project_stats: dict


@router.post("/ask", response_model=QuestionResponse)
async def ask_question(
    request: QuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ask a question about documents in a project"""
    
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == request.project_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    try:
        # Query RAG pipeline
        result = rag_pipeline.query(request.question, request.project_id)
        
        # Get project stats
        project_stats = rag_pipeline.get_project_stats(request.project_id)
        
        return QuestionResponse(
            answer=result["answer"],
            sources=result["sources"],
            project_stats=project_stats
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing question: {str(e)}"
        )


@router.get("/projects/{project_id}/stats")
async def get_project_stats(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get statistics for a project"""
    
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    try:
        stats = rag_pipeline.get_project_stats(project_id)
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting project stats: {str(e)}"
        )


@router.post("/projects/{project_id}/summarize")
async def summarize_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a summary of all documents in a project"""
    
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    try:
        # Ask for a comprehensive summary
        summary_question = "Please provide a comprehensive summary of all the papers in this project. Include the main topics, key findings, methodologies used, and any important insights. Organize the summary in a clear and structured way."
        
        result = rag_pipeline.query(summary_question, project_id)
        
        return {
            "summary": result["answer"],
            "sources": result["sources"],
            "project_name": project.name
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating summary: {str(e)}"
        )


@router.post("/projects/{project_id}/compare")
async def compare_papers(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Compare papers in a project"""
    
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    try:
        # Ask for a comparison
        comparison_question = "Please compare and contrast the papers in this project. Highlight similarities and differences in methodologies, findings, and approaches. Identify any gaps or areas where the papers complement each other."
        
        result = rag_pipeline.query(comparison_question, project_id)
        
        return {
            "comparison": result["answer"],
            "sources": result["sources"],
            "project_name": project.name
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating comparison: {str(e)}"
        )
