from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from dataAPI import models, schemas
from dataAPI.db_connection import SessionLocal, engine
from dataAPI.jira_api import fetch_jira_data

models.Base.metadata.create_all(bind=engine)

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@app.get("/records/", response_model=List[schemas.Ticket])
def show_records(db: Session = Depends(get_db)):
    records = db.query(models.Ticket).all()
    return records

@app.get("/export/")
def export(db: Session = Depends(get_db)):
    cleaned_issues, cleaned_worklogs = fetch_jira_data('\'Platforms Team\'')
    
    for i in cleaned_issues:
        db.add(i)
    for w in cleaned_worklogs: 
        db.add(w)
    db.commit()
    return "Done!"
    

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app:app", port=8080, log_level="info")