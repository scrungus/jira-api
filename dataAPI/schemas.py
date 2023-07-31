from datetime import date
from pydantic import BaseModel
from typing import Optional

from datetime import datetime, timedelta


class Ticket(BaseModel):
    id: int
    key: str
    project: str
    issuetype: str
    priority: str
    summary: str
    customer: Optional[str]
    status: str
    assignee: Optional[str]
    epic_name: Optional[str]
    epic_link: Optional[str]
    parent: Optional[str]

    class Config:
        orm_mode = True

class WorkLog(BaseModel):
    id: int
    started: datetime
    updated: datetime
    name: str
    work_des: Optional[str]
    time_spent: int
    ticket_id: int
    epic_id: int

    class Config:
        orm_mode = True

class WorkLogChangeLog(BaseModel):
    id: int
    worklog_id : int
    prev_started: datetime
    new_started: Optional[datetime]
    updated: datetime
    name: str
    work_des: Optional[str]
    prev_time_spent: int
    new_time_spent: Optional[int]
    ticket_id: int

    class Config:
        orm_mode = True