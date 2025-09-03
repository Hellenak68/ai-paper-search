from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import asyncio
from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.file import File as FileModel
from app.models.project import Project
from app.api.users import get_current_user
from app.services.file_processing import pdf_processor
from app.services.rag_pipeline import rag_pipeline

router = APIRouter()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    project_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and process a PDF file"""
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Validate file size
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {settings.max_file_size} bytes"
        )
    
    # Reset file pointer
    await file.seek(0)
    
    try:
        # Save file to disk
        file_path, unique_filename = await pdf_processor.save_uploaded_file(
            file, settings.upload_dir
        )
        
        # Create file record in database
        db_file = FileModel(
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=file.content_type,
            owner_id=current_user.id,
            project_id=project_id,
            processing_status="processing"
        )
        
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        # Process file asynchronously
        asyncio.create_task(process_file_async(db_file.id, project_id))
        
        return {
            "id": db_file.id,
            "filename": db_file.original_filename,
            "file_size": db_file.file_size,
            "status": db_file.processing_status,
            "project_id": project_id
        }
        
    except Exception as e:
        # Clean up file if processing fails
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File processing failed: {str(e)}"
        )


async def process_file_async(file_id: int, project_id: Optional[int]):
    """Process file asynchronously in background"""
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    try:
        # Get file record
        db_file = db.query(FileModel).filter(FileModel.id == file_id).first()
        if not db_file:
            return
        
        try:
            # Process PDF
            result = pdf_processor.process_pdf(db_file.file_path)
            
            # Add to RAG pipeline if project_id is provided
            if project_id:
                rag_pipeline.add_documents_to_project(
                    result["chunks"], file_id, project_id
                )
            
            # Update file status
            db_file.is_processed = True
            db_file.processing_status = "completed"
            db.commit()
            
        except Exception as e:
            # Update file status to failed
            db_file.processing_status = "failed"
            db.commit()
            print(f"Error processing file {file_id}: {str(e)}")
    
    finally:
        db.close()


@router.get("/")
async def get_files(
    project_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get files for current user, optionally filtered by project"""
    query = db.query(FileModel).filter(FileModel.owner_id == current_user.id)
    
    if project_id:
        query = query.filter(FileModel.project_id == project_id)
    
    files = query.all()
    
    return [
        {
            "id": file.id,
            "filename": file.original_filename,
            "file_size": file.file_size,
            "is_processed": file.is_processed,
            "processing_status": file.processing_status,
            "project_id": file.project_id,
            "created_at": file.created_at
        }
        for file in files
    ]


@router.get("/{file_id}")
async def get_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific file"""
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.owner_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return {
        "id": file.id,
        "filename": file.original_filename,
        "file_size": file.file_size,
        "is_processed": file.is_processed,
        "processing_status": file.processing_status,
        "project_id": file.project_id,
        "created_at": file.created_at
    }


@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a file"""
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.owner_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Delete physical file
    if os.path.exists(file.file_path):
        os.remove(file.file_path)
    
    # Delete from database
    db.delete(file)
    db.commit()
    
    return {"message": "File deleted successfully"}
