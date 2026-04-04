from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from app.routers import analytics

app = FastAPI(
    title="Analytics Service",
    description="Aggregates financial data to provide insights: summaries, trends, and budget status",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "analytics-service"}
