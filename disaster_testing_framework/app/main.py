from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.models.base import Base
from app.routes import api, testing, portal

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Disaster Management Portal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(portal.router)
app.include_router(api.router)
app.include_router(testing.router)
