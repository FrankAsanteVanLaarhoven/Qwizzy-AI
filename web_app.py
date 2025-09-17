from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


app = FastAPI(title="Interview Intelligence Platform")

# Mount static files (CSS/JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates directory for HTML
templates = Jinja2Templates(directory="templates")


@app.get("/healthz", response_class=JSONResponse)
async def health_check() -> dict:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Interview Intelligence Platform"},
    )


