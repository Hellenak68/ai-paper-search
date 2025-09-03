# RAG Paper Search

AI-powered paper search and summarization chatbot for researchers. Upload PDF papers and ask questions in both English and Korean to get instant insights and summaries.

## Features

- **PDF Upload & Processing**: Drag-and-drop PDF upload with automatic text extraction
- **AI-Powered Q&A**: Ask questions about your papers in English or Korean
- **Project Management**: Organize papers into projects for better management
- **Citation & Highlighting**: Get answers with source citations and page references
- **Real-time Processing**: Fast response times with streaming answers
- **Bilingual Support**: Seamless English ↔ Korean translation

## Tech Stack

- **Backend**: Python 3.11, FastAPI, LangChain
- **Vector DB**: FAISS (in-memory)
- **Database**: SQLite
- **AI**: Upstage Solar-1-mini-chat, Solar Embeddings
- **Frontend**: HTMX, Alpine.js, Tailwind CSS
- **Deployment**: Docker, Render.com/Fly.io

## Quick Start

### Prerequisites

- Python 3.11+
- Upstage API key
- Docker (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-paper-search
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   **옵션 1: 환경 변수 사용 (권장)**
   ```bash
   # Windows
   set UPSTAGE_API_KEY=your_api_key_here
   
   # Linux/Mac
   export UPSTAGE_API_KEY=your_api_key_here
   ```
   
   **옵션 2: .env 파일 사용**
   ```bash
   cp env.example .env
   # Edit .env with your Upstage API key
   ```
   
   **옵션 3: 런타임 입력**
   ```bash
   # API 키 없이 실행하면 안전한 입력 프롬프트가 나타남
   uvicorn app.main:app --reload
   ```

4. **Initialize database**
   ```bash
   python -m app.core.init_db
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Access the application**
   Open your browser and go to `http://localhost:8000`

### Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Access the application**
   Open your browser and go to `http://localhost:8000`

## Usage

### 1. Create a Project
- Click "New Project" on the dashboard
- Enter project name and description
- Click "Create"

### 2. Upload PDFs
- Open your project
- Click "Upload PDF"
- Select PDF files to upload
- Wait for processing to complete

### 3. Ask Questions
- Use the Q&A interface in your project
- Ask questions in English or Korean
- Get instant answers with source citations

### Example Questions
- "What are the main findings of these papers?"
- "핵심 기여를 3줄로 요약해줘"
- "Compare the methodologies used"
- "What are the limitations mentioned?"

## API Endpoints

### Authentication
- `POST /api/users/register` - Register new user
- `POST /api/users/login` - Login user
- `GET /api/users/me` - Get current user info

### Projects
- `GET /api/projects/` - Get user projects
- `POST /api/projects/` - Create new project
- `GET /api/projects/{id}` - Get project details
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project

### Files
- `POST /api/files/upload` - Upload PDF file
- `GET /api/files/` - Get user files
- `GET /api/files/{id}` - Get file details
- `DELETE /api/files/{id}` - Delete file

### Q&A
- `POST /api/qa/ask` - Ask question about project
- `GET /api/qa/projects/{id}/stats` - Get project statistics
- `POST /api/qa/projects/{id}/summarize` - Generate project summary
- `POST /api/qa/projects/{id}/compare` - Compare papers in project

## Configuration

Key configuration options in `.env`:

```env
UPSTAGE_API_KEY=your_upstage_api_key_here
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///./app.db
MAX_FILE_SIZE=52428800  # 50MB
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

## Development

### Project Structure
```
app/
├── api/           # API endpoints
├── core/          # Core configuration and database
├── models/        # Database models
├── services/      # Business logic (RAG pipeline, file processing)
├── templates/     # HTML templates
├── static/        # Static files (CSS, JS)
└── utils/         # Utility functions
```

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black app/
isort app/
```

## Deployment

### Render.com
1. Connect your GitHub repository
2. Set environment variables
3. Deploy automatically

### Fly.io
1. Install flyctl
2. Run `fly launch`
3. Set secrets: `fly secrets set UPSTAGE_API_KEY=your_key`
4. Deploy: `fly deploy`

## Performance

- **Response Time**: < 5 seconds average
- **Throughput**: 500 Q&A requests per day
- **File Size Limit**: 50MB per PDF
- **Translation Quality**: BLEU ≥ 35

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation
- Contact the development team

---

Built with ❤️ for researchers who want to analyze papers faster and more efficiently.
