from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from sqlalchemy import text

from dataAPI import models, schemas
from dataAPI.db_connection import SessionLocal, engine
from dataAPI.jira_api import fetch_jira_data, get_issue, get_children
import csv
import json
import logging
from datetime import datetime,timezone
from dateutil import parser

models.Base.metadata.create_all(bind=engine)
# models.WorkLogChangeLog.__table__.drop(engine)
# models.WorkLog.__table__.drop(engine)
# models.Ticket.__table__.drop(engine)
# models.Employee.__table__.drop(engine)


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

@app.on_event("startup")
async def startup_event():
    logger = logging.getLogger("uvicorn.access")
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)

@app.get("/issues/", response_model=List[schemas.Ticket])
def show_issues(db: Session = Depends(get_db)):
    records = db.query(models.Ticket).all()
    with open('issues.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        for r in records:
            writer.writerow([r.project,r.key,r.epic_name])
    return records

@app.get("/issue/", response_model=schemas.Ticket)
def show_issues():
    return get_issue(15866)

@app.get("/children/", response_model=schemas.Ticket)
def show_child_issues():
    return get_children('BT-15')

@app.get("/worklog/", response_model=List[schemas.WorkLog])
def worklog(db: Session = Depends(get_db)):
    records = db.query(models.WorkLog).all()
    return records

@app.get("/worklogs/", response_model=List[schemas.WorkLog])
def show_worklogs(db: Session = Depends(get_db)):
    start = datetime(day=1,month=4,year=2023)
    end = datetime(day=30,month=4,year=2023) 
    records = db.query(models.WorkLog).filter(models.WorkLog.started>=start, models.WorkLog.started<=end).all()
    # fields = ['Project','Issue Type', 'Key', 'Summary', 'Priority', 'Assignee','Epic Name','Customer','Date Started','Display Name', 'Time Spent (h)', 'Work Description']

    # with open('worklogs.csv', 'w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerow(fields)
    #     for r in records:
    #         ticket = db.query(models.Ticket).filter_by(id=r.epic_id).first()
    #         row = [ticket.project,ticket.issuetype,ticket.key,ticket.summary,ticket.priority, ticket.assignee, ticket.epic_name, ticket.customer, r.started, r.name, r.time_spent/3600, r.work_des]
    #         writer.writerow(row)

    # ids = set() 
    # for r in records:
    #     if (r.started > start and r.started < end) or (r.updated > start and r.updated < end):
    #         ids.add(r.ticket_id)
    # totsum = 0
    # for i in ids: 
    #     entry = db.query(models.Ticket).filter_by(id=i).first()
    #     print(entry.summary)
    #     print(entry.customer)
    #     print(entry.key)
    #     sum = 0
    #     for r in records:
    #         if r.ticket_id == i:
    #             sum += r.time_spent
    #             totsum += r.time_spent
    #     print(sum/3600)
    #     print('---------------------')
    # print("issue count",len(ids))
    # print("total hours:",totsum/3600)
    return records

@app.get("/changes/", response_model=List[schemas.WorkLogChangeLog])
def show_changes(db: Session = Depends(get_db)):
    records = db.query(models.WorkLogChangeLog).all()
    return records

@app.get("/employees/")
def employees(db: Session = Depends(get_db)):
    with open('/Users/tcee/Documents/code/jira-app/dataAPI/Roles.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            db.merge(
                models.Employee(
                    name = row[0],
                    role = row[1],
                    rate_card_description = row[2],
                    hours_pw = row[3],
                    start_date = parser.parse(row[4], dayfirst=True),
                    end_date = parser.parse(row[5], dayfirst=True) if row[5] != '' else None
                )
            )
        db.commit()
    records = db.query(models.Employee).all()
    return records

@app.get("/export/")
def export(db: Session = Depends(get_db)):
    projects = [
        '\'Platforms Team\'',
        'DEV',
        'RT',
        'INFRA',
        'SHPC',
        'GT',
        'BT',
        'PIP'
    ]
    for p in projects: 
        print("Waiting for Jira API (project ",p,")...")
        cleaned_issues, cleaned_worklogs = fetch_jira_data(p)
        
        for i in cleaned_issues:
            #print("merging issue ",i.id)
            db.merge(i)
        for iter,w in enumerate(cleaned_worklogs): 
            # entry = db.query(models.WorkLog).filter_by(id=w.id).first()
            # print("merging worklog for ticket",w.ticket_id)
            # if entry is not None:
            #     if w.updated.astimezone(timezone.utc).replace(tzinfo=None) != entry.updated:
            #         print("worklog changed!")
            #         print('w.updated',w.updated.astimezone(timezone.utc).replace(tzinfo=None))
            #         print('entry.updated',entry.updated)
            #         db.add(models.WorkLogChangeLog(
            #             worklog_id = w.id,
            #             updated = w.updated,
            #             prev_started = entry.started,
            #             new_started = w.started if w.started!=entry.started else None,
            #             prev_time_spent = entry.time_spent,
            #             new_time_spent = w.time_spent if w.time_spent!=entry.time_spent else None,
            #             ticket_id = w.ticket_id,
            #         ))
            db.merge(w)
            if iter%250 == 0:
                print('flushing')
                db.commit()
        db.commit()
    return "Done!"
    

import uvicorn

log_config = uvicorn.config.LOGGING_CONFIG
log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
log_config["formatters"]["default"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"

if __name__ == "__main__":
    uvicorn.run("app:app", port=8080, log_level="info", reload=True)