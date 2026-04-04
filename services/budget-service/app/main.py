from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from app.database import engine, Base
from app.routers import budgets

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Budget Service",
    description="Manages budget goals and spending alerts",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)
app.include_router(budgets.router, prefix="/api/budgets", tags=["budgets"])

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "budget-service"}
