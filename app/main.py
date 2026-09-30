from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routes import router
from app.database import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FitBuddy - AI Fitness Plan Generator",
    description="AI-powered workout and nutrition planner using Gemini models",
    version="1.0.0"
)

# Include application routes
app.include_router(router)
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


# Serve static files (CSS, images, JS)
app.mount("/static", StaticFiles(directory="static", check_dir=False), name="static")


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "FitBuddy",
        "version": "1.0.0"
    }