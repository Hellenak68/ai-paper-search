from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.models.project import Project
from app.api.users import get_current_user

router = APIRouter()


@router.post("/")
async def create_project(
    name: str,
    description: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new project"""
    project = Project(
        name=name,
        description=description,
        owner_id=current_user.id
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "created_at": project.created_at
    }


@router.get("/")
async def get_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all projects for current user"""
    projects = db.query(Project).filter(Project.owner_id == current_user.id).all()
    
    return [
        {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "created_at": project.created_at,
            "file_count": len(project.files)
        }
        for project in projects
    ]


@router.get("/{project_id}")
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific project"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "created_at": project.created_at,
        "files": [
            {
                "id": file.id,
                "filename": file.filename,
                "original_filename": file.original_filename,
                "file_size": file.file_size,
                "is_processed": file.is_processed,
                "created_at": file.created_at
            }
            for file in project.files
        ]
    }


@router.put("/{project_id}")
async def update_project(
    project_id: int,
    name: str = None,
    description: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a project"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if name is not None:
        project.name = name
    if description is not None:
        project.description = description
    
    db.commit()
    db.refresh(project)
    
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "updated_at": project.updated_at
    }


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a project"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    db.delete(project)
    db.commit()
    
    return {"message": "Project deleted successfully"}
