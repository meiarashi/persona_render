from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, Response, FileResponse
from pathlib import Path
import json
import os
import random
import traceback
import io
import re
from urllib.parse import quote
from urllib.request import urlopen
import base64

# For PDF/PPT generation
from PIL import Image
from fpdf import FPDF
from pptx import Presentation
from pptx.util import Inches, Pt, Cm
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_AUTO_SIZE
from pptx.enum.text import MSO_VERTICAL_ANCHOR

# For AI clients
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# New Gemini SDK (preferred)
try:
    from google import genai as google_genai_sdk # Alias to avoid conflict
    from google.genai import types as google_genai_types
except ImportError:
    google_genai_sdk = None
    google_genai_types = None

# Old Gemini SDK (fallback)
try:
    import google.generativeai as old_gemini_sdk
except ImportError:
    old_gemini_sdk = None
    
try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

# Import from new structure
from api import admin_settings
from services import crud, rag_processor
from models import schemas

# Create a FastAPI app instance
app = FastAPI(
    title="Persona Render Admin API",
    description="API for managing Persona Render application settings.",
    version="0.1.0"
)

# Mount the admin_settings router
app.include_router(admin_settings.router)

# --- Static files hosting ---
current_file_dir = Path(__file__).resolve().parent
project_root_dir = current_file_dir.parent
frontend_dir = project_root_dir / "frontend"

# Check for assets directory in new structure
assets_dir = project_root_dir / "assets"

if not frontend_dir.exists() or not frontend_dir.is_dir():
    alt_frontend_dir = project_root_dir / "frontend"
    if (project_root_dir / "backend").exists() and (project_root_dir / "frontend").exists():
        frontend_dir = project_root_dir / "frontend"
    else:
        frontend_dir = current_file_dir / "frontend"

if frontend_dir.exists() and frontend_dir.is_dir():
    print(f"Serving static files from: {frontend_dir}")
    app.mount("/static/user", StaticFiles(directory=frontend_dir / "user"), name="user_static_assets")
    app.mount("/static/admin", StaticFiles(directory=frontend_dir / "admin"), name="admin_static_assets")
    
    # Mount assets directory (new structure)
    if assets_dir.exists() and assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
        print(f"Serving assets from: {assets_dir}")
    
    # Legacy images directory support
    images_dir = project_root_dir / "images"
    if images_dir.exists() and images_dir.is_dir():
        app.mount("/images", StaticFiles(directory=images_dir), name="image_assets")
        print(f"Serving image files from: {images_dir}")

    @app.get("/admin", include_in_schema=False)
    async def serve_admin_html():
        admin_html_path = frontend_dir / "admin/admin.html"
        if admin_html_path.exists(): return FileResponse(admin_html_path)
        fallback_html_path = project_root_dir / "frontend/admin/admin.html"
        if fallback_html_path.exists(): return FileResponse(fallback_html_path)
        raise HTTPException(status_code=404, detail="admin.html not found")

    @app.get("/", include_in_schema=False)
    async def serve_user_html():
        user_html_path = frontend_dir / "user/index.html"
        if user_html_path.exists(): return FileResponse(user_html_path)
        fallback_html_path = project_root_dir / "frontend/user/index.html"
        if fallback_html_path.exists(): return FileResponse(fallback_html_path)
        raise HTTPException(status_code=404, detail="index.html not found")
else:
    print(f"WARNING: Frontend directory not found at {frontend_dir}. Static files will not be served.")

# Helper function to find font file
def find_font_file():
    """Search for the Japanese font file in various locations"""
    possible_paths = [
        project_root_dir / "assets" / "fonts" / "ipaexg.ttf",  # New structure
        project_root_dir / "ipaexg.ttf",  # Legacy location
        current_file_dir / "ipaexg.ttf",
        Path("/usr/share/fonts/truetype/fonts-japanese-gothic.ttf"),
        Path("/usr/share/fonts/truetype/fonts-japanese-mincho.ttf"),
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path)
    
    # Default fallback
    return str(project_root_dir / "assets" / "fonts" / "ipaexg.ttf")

# Get font path
FONT_PATH = find_font_file()
print(f"Using font from: {FONT_PATH}")

# Note: This is a minimal version for testing the new structure.
# The full implementation with all endpoints will be added after confirming the structure works.

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "structure": "new"}

# Error handler
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    error_trace = traceback.format_exc()
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "traceback": error_trace
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)