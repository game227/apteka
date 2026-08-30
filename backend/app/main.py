from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routers import admin, auth, drugs, pharmacy, prescriptions

settings = get_settings()

app = FastAPI(title="Dori narxlari platformasi API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(drugs.router)
app.include_router(prescriptions.router)
app.include_router(pharmacy.router)
app.include_router(admin.router)


@app.get("/health")
def health():
    return {"status": "ok"}


# Frontend'ning build qilingan SPA'sini xuddi shu portda serve qilish
# (bitta-port dev/demo rejimi uchun — Railway'da alohida service bo'lishi mumkin).
_FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if _FRONTEND_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=_FRONTEND_DIST / "assets"), name="frontend-assets")

    @app.get("/{full_path:path}")
    def spa_fallback(full_path: str):
        candidate = _FRONTEND_DIST / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(_FRONTEND_DIST / "index.html")
