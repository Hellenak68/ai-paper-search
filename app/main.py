from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.api import users, projects, files, qa

# Initialize FastAPI app
app = FastAPI(
    title="RAG Paper Search",
    description="AI-powered paper search and summarization chatbot",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Include API routers
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(qa.router, prefix="/api/qa", tags=["qa"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()


@app.get("/")
async def root(request: Request):
    """Root endpoint - serve dashboard"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/project/{project_id}")
async def project_page(project_id: int, request: Request):
    """Project page endpoint"""
    return templates.TemplateResponse("project.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
