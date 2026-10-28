from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.config import settings
from backend.database import check_db_connection
from backend.routers import (
    overview,
    sales,
    customers,
    inventory,
    logistics,
    reviews,
    ai_insights,
    geography,
    ai_chat,
    simulator,
    export
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Full-stack AI-Driven E-Commerce Intelligence & Decision Support Platform",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for external dashboards or development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(overview.router)
app.include_router(sales.router)
app.include_router(customers.router)
app.include_router(inventory.router)
app.include_router(logistics.router)
app.include_router(reviews.router)
app.include_router(ai_insights.router)
app.include_router(geography.router)
app.include_router(ai_chat.router)
app.include_router(simulator.router)
app.include_router(export.router)

# Health Check Endpoint
@app.get("/health", tags=["System Health"])
def health_check():
    db_ok, db_msg = check_db_connection()
    return {
        "status": "healthy" if db_ok else "degraded",
        "database": {
            "connected": db_ok,
            "message": db_msg,
            "host": settings.DB_HOST,
            "database_name": settings.DB_NAME
        },
        "version": settings.PROJECT_VERSION
    }

# Disable browser caching for frontend assets in development
@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    if request.url.path == "/" or request.url.path.startswith("/static"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Static files and frontend dashboard
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Mount static assets
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/", tags=["Frontend"])
def serve_dashboard():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(
            index_file,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    return {
        "message": "OmniPulse E-Commerce Intelligence API is running. Access interactive documentation at /docs."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
