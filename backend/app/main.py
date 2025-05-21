from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Import the router from the routers module
from .routers import admin_settings # Assuming admin_settings.py is in a 'routers' subdirectory

# Create a FastAPI app instance
app = FastAPI(
    title="Persona Render Admin API",
    description="API for managing Persona Render application settings.",
    version="0.1.0"
)

# Mount the admin_settings router
app.include_router(admin_settings.router)

# --- Static files hosting (for admin.html, admin_script.js, admin_style.css) ---
# Determine the path to the frontend directory relative to this main.py file.

# Path to the directory where this main.py file is located (e.g., .../backend/app/)
current_file_dir = Path(__file__).resolve().parent
# Path to the 'backend' directory (e.g., .../backend/)
backend_dir = current_file_dir.parent
# Path to the root of the project (e.g., .../)
project_root_dir = backend_dir.parent
# Path to the 'frontend' directory (e.g., .../frontend/)
frontend_dir = project_root_dir / "frontend"

# Check if a common alternative structure is used (e.g. backend and frontend are siblings)
# If not, try to find frontend relative to project root or specific locations.
# This logic might need adjustment based on the *actual* project structure.

# A more robust way to locate frontend if it's not strictly 'sibling to backend':
# Attempt 1: Frontend as a sibling to the backend directory's parent (common for repo root)
# Example: repo_root/frontend and repo_root/backend/app/main.py
if not frontend_dir.exists() or not frontend_dir.is_dir():
    # Attempt 2: Frontend directory directly in the project root (where backend might also be)
    # Example: repo_root/frontend and repo_root/backend (main.py inside backend or backend/app)
    # This assumes backend_dir is .../backend/
    # If project_root_dir is actually the repo root: project_root_dir / 'frontend'
    alt_frontend_dir = project_root_dir / "frontend" # Default assumption
    if (project_root_dir / "backend").exists() and (project_root_dir / "frontend").exists():
        frontend_dir = project_root_dir / "frontend"
    elif (backend_dir.parent / "frontend").exists(): # if backend is one level down from root
         frontend_dir = backend_dir.parent / "frontend"
    else: # Final fallback if backend_dir is the root
        frontend_dir = backend_dir / "frontend"


if frontend_dir.exists() and frontend_dir.is_dir():
    print(f"Serving static files from: {frontend_dir}")
    
    # Serve admin_script.js and admin_style.css from /static route, pointing to the frontend_dir directly
    # So, if admin_script.js is at frontend_dir/admin_script.js, it's accessible via /static/admin_script.js
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static_assets")

    @app.get("/", include_in_schema=False)
    async def serve_admin_html():
        from fastapi.responses import FileResponse
        admin_html_path = frontend_dir / "admin.html"
        if admin_html_path.exists():
            return FileResponse(admin_html_path)
        # If admin.html is not in frontend_dir, try project_root_dir as a fallback for very flat structures
        # This is less common for organized projects.
        fallback_html_path = project_root_dir / "admin.html"
        if fallback_html_path.exists():
            return FileResponse(fallback_html_path)
        raise HTTPException(status_code=404, detail=f"admin.html not found in {frontend_dir} or {project_root_dir}")

    print(f"Admin UI (admin.html) should be available at the root path ('/').")
    print(f"Static files (e.g., admin_script.js) are served from '/static'. E.g., /static/admin_script.js")

else:
    print(f"Frontend directory not found at expected location: {frontend_dir} (or alternatives tried). Ensure your 'frontend' directory containing admin.html, admin_script.js, etc., is correctly placed relative to the backend app or define FRONTEND_DIR_PATH environment variable.")
    print("Static file serving for admin UI will be skipped.")

@app.get("/health", summary="Health check endpoint", tags=["Health"])
async def health_check():
    """
    Simple health check endpoint to confirm the API is running.
    """
    return {"status": "ok"}

# To run this app locally (from the 'backend' directory, assuming main.py is in 'app'):
# Ensure 'app' is a package (has __init__.py if needed, though often not for FastAPI structure like this)
# cd backend
# python -m uvicorn app.main:app --reload --port 8000

# If your structure is flatter, e.g. main.py in 'backend' root:
# cd backend
# uvicorn main:app --reload --port 8000 