from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.config import settings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def _get_context(request: Request, title: str):
    return {
        "request": request,
        "title": title,
        "demo_mode": not bool(settings.anthropic_api_key)
    }

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", _get_context(request, "Dashboard - AI Email Assistant"))

@router.get("/history", response_class=HTMLResponse)
async def read_history(request: Request):
    return templates.TemplateResponse("history.html", _get_context(request, "History - AI Email Assistant"))

@router.get("/about", response_class=HTMLResponse)
async def read_about(request: Request):
    return templates.TemplateResponse("about.html", _get_context(request, "About - AI Email Assistant"))
