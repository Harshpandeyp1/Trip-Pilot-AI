import os
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load local environment settings
load_dotenv()

# Add project root and backend folder to python path to resolve imports correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from backend.api.routes import router as api_router

app = FastAPI(
    title="TripPilot AI – Offline Smart Travel Planner",
    description="A multi-agent travel planner utilizing Google ADK and MCP local datasets.",
    version="1.0.0"
)

# Enable CORS for local React development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In development, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount endpoints under /api
app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "mode": "100% offline",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    
    print(f"Starting TripPilot AI Backend on http://{host}:{port}")
    print("Run frontend via: npm run dev (inside frontend/)")
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)
