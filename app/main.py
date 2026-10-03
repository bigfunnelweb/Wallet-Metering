
from fastapi import FastAPI

from app.database import Base, engine
from app import models
from app.routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MeterPay",
    description="Wallet-based API metering service",
    version="1.0.0",
)

app.include_router(router)


@app.get("/")
def home():
    return {"message": "Welcome to MeterPay API"}