"""
main.py — LendFlow FinOps Framework FastAPI Application Entrypoint
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.backend.routers import (
    summary, explorer, optimisations, storage,
    transfer, tags, anomalies, simulator, war_room
)

app = FastAPI(
    title="LendFlow FinOps Framework API",
    description=(
        "Production-grade FinOps & Cloud Cost Optimization API for LendFlow Technologies. "
        "Engineered for AWS Cost Optimization, Compliance Guardrails & Unit Economics."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware for frontend integration (React + Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all 8 core FinOps Routers
app.include_router(summary.router)
app.include_router(explorer.router)
app.include_router(optimisations.router)
app.include_router(storage.router)
app.include_router(transfer.router)
app.include_router(tags.router)
app.include_router(anomalies.router)
app.include_router(simulator.router)
app.include_router(war_room.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "framework": "LendFlow FinOps Framework",
        "author": "FinOps & Cloud Architecture Engineering Team",
        "version": "1.0.0",
        "status": "OPERATIONAL",
        "docs": "/docs",
        "endpoints": {
            "summary": "/api/summary",
            "explorer": "/api/explorer",
            "optimisations": "/api/optimisations",
            "storage": "/api/storage",
            "transfer": "/api/transfer",
            "tags": "/api/tags",
            "anomalies": "/api/anomalies",
            "simulator": "/api/simulator",
            "war_room": "/api/war-room"
        }
    }


@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "HEALTHY",
        "region": "ap-south-1",
        "version": "1.0.0"
    }
