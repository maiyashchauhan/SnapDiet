import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import auth, diet, ai

app = FastAPI(title="SnapDiet API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(diet.router, prefix="/api/diet", tags=["diet"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])

@app.get("/")
def read_root():
    return {"message": "SnapDiet API is running"}
