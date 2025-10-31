from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

router = APIRouter()

# Configure templates directory
templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "dashboard", "templates")
templates = Jinja2Templates(directory=templates_dir)

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Serve the main dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/dashboard/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Serve the login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/dashboard/users", response_class=HTMLResponse)
async def users_page(request: Request):
    """Serve the users management page"""
    return templates.TemplateResponse("users.html", {"request": request})

@router.get("/dashboard/content", response_class=HTMLResponse)
async def content_page(request: Request):
    """Serve the content management page"""
    return templates.TemplateResponse("content.html", {"request": request})

@router.get("/dashboard/posts", response_class=HTMLResponse)
async def posts_page(request: Request):
    """Serve the posts management page"""
    return templates.TemplateResponse("posts.html", {"request": request})

@router.get("/dashboard/config", response_class=HTMLResponse)
async def config_page(request: Request):
    """Serve the configuration page"""
    return templates.TemplateResponse("config.html", {"request": request})

@router.get("/dashboard/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    """Serve the analytics page"""
    return templates.TemplateResponse("analytics.html", {"request": request})