from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import get_db
from routers.sources import router as sources_router
from routers.articles import router as articles_router

app = FastAPI(title="RSS-GPT API")

app.include_router(sources_router)
app.include_router(articles_router)

@app.get("/")
def read_root():
    return {"message": "RSS-GPT API is running."}