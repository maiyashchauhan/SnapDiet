import os, sys

# Ensure api directory, api/utils, and repo root are in python path
current_dir = os.path.dirname(__file__)
root_dir = os.path.dirname(current_dir)

for path in [current_dir, os.path.join(current_dir, "utils"), root_dir]:
    if path not in sys.path:
        sys.path.insert(0, path)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse

try:
    from api.routes import auth, diet, ai
except ModuleNotFoundError:
    from routes import auth, diet, ai

app = FastAPI(
    title="SnapDiet API",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "InternalServerError", "detail": str(exc), "path": request.url.path}
    )

# Support routes with and without /api prefix for public rewrites and internal bindings
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])

app.include_router(diet.router, prefix="/api/diet", tags=["diet"])
app.include_router(diet.router, prefix="/diet", tags=["diet"])

app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])

@app.get("/")
@app.get("/api")
@app.get("/api/")
def read_root():
    return {"message": "SnapDiet API is running", "status": "healthy", "docs": "/api/docs"}

@app.get("/api/docs", include_in_schema=False)
def redirect_api_docs():
    return RedirectResponse(url="/docs")

@app.get("/api/openapi.json", include_in_schema=False)
def redirect_api_openapi():
    return RedirectResponse(url="/openapi.json")
