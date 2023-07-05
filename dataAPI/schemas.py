from datetime import date
from pydantic import BaseModel
from typing import Optional

from datetime import datetime, timedelta


class Ticket(BaseModel):
    id: int
    key: str
    issuetype: str
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
    ticket_id: int
    name: str
    started: datetime
    time_spent: timedelta
    work_des: str