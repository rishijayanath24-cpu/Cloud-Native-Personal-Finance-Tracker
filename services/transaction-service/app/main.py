from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from app.database import engine, Base
from app.routers import transactions

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Transaction Service",
    description="Manages financial transactions - income and expenses",
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
app.include_router(transactions.router, prefix="/api/transactions", tags=["transactions"])

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "transaction-service"}
