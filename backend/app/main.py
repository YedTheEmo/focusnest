from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import pathlib

from .database import init_db
from .api import notes, graph, search

# Create FastAPI app
app = FastAPI(title="FocusNest API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Include API routers
app.include_router(notes.router, prefix="/api")
app.include_router(graph.router, prefix="/api")
app.include_router(search.router, prefix="/api")

# Resolve project and frontend paths
def _get_frontend_path() -> pathlib.Path:
    # __file__ -> backend/app/main.py
    project_root = pathlib.Path(__file__).parents[2]
    return project_root / "frontend"

frontend_path = _get_frontend_path()

# Mount static files
app.mount(
    "/static",
    StaticFiles(directory=str(frontend_path)),
    name="static",
)

@app.get("/")
async def serve_frontend():
    index_file = frontend_path / "index.html"
    return FileResponse(str(index_file))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "FocusNest API is running"}

