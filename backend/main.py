import os
import sys

# Add the root 'Aegis-Recon' directory to sys.path so 'backend' module is recognized
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.api import routes, agent
app = FastAPI(title="Argus Command API v2.0")

# Mount Static Files
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')
STATIC_DIR = os.path.join(FRONTEND_DIR, 'static')

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Mount API Router
app.include_router(routes.router, prefix="/api/v1")
app.include_router(agent.router, prefix="/api/v1")

@app.get("/")
def read_index():
    return FileResponse(os.path.join(FRONTEND_DIR, 'index.html'))

if __name__ == "__main__":
    import uvicorn
    # Typically running on 0.0.0.0 for external access if needed, but 127.0.0.1 locally is fine.
    # Defaulting to 8000
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
