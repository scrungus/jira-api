import json
from jira import JIRA
from jira.client import ResultList
from jira.resources import Issue, TimeTracking
from typing import cast
from dateutil import parser
from datetime import timedelta
import dataAPI.models as models
import logging
import sys

LOG = logging.getLogger("uvicorn.access")


def get_issue(issue_key):
    file = "config.json"
    config = json.load(open(file))

    jira = JIRA(
        options={'server': config['url']},
        basic_auth=(config['user'], config['password'])
    )
    
    issue= jira.issue(issue_key)
    print("ISSUE::")
    print(issue.key)
    print(issue.raw['fields'])
    return issue

def get_children(issue_key):
    file = "config.json"
    config = json.load(open(file))

    jira = JIRA(
        options={'server': config['url']},
        basic_auth=(config['user'], config['password'])
    )
    
    issues = jira.search_issues(f'parent={issue_key}', maxResults=0)
    print("ISSUES::")
    for i in issues: 
        print(i.key)
        worklogs = jira.worklogs(i.key)
        for w in worklogs:
            print(parser.parse(w.raw['started']))
            print(w.raw['timeSpentSeconds']/3600)
            
    print(len(issues))

def fetch_jira_data(project):

    file = "config.json"
    config = json.load(open(file))

    jira = JIRA(
        options={'server': config['url']},
        basic_auth=(config['user'], config['password'])
    )

    def get_all_epics(jira_client, project_name, fields):
        issues = []
        i = 0
        chunk_size = 100
        #while True:
        chunk = jira_client.search_issues(f'issuetype=Epic', startAt=i, maxResults=0)
            # i += chunk_size
        issues += chunk.iterable
            # if i >= chunk.total:
            #     break
        print(len(issues))
        return issues

    epics = cast(ResultList[Issue], get_all_epics(jira, project, ["id", "fixVersion"]))
    cleaned_issues = []
    cleaned_worklogs = []

    for i in epics:
        if hasattr(i.fields,'parent') and i.fields.parent is not None:
            parent_id = i.fields.parent.id
        else:
            parent_id = None
        
        if hasattr(i.fields,'assignee') and i.fields.assignee is not None:
            assignee_name = i.fields.assignee.displayName
        else:
            assignee_name = None

        cleaned_issues.append(models.Ticket(
            id=i.id,
            key=i.key,
            project=i.fields.project.raw['name'],
            issuetype = i.fields.issuetype.name,
            priority = i.fields.priority.raw['name'],
            summary = i.fields.summary,
            status = i.fields.status.name,
            customer = i.fields.customfield_10026 if hasattr(i.fields,'customfield_10026') else None,
            assignee = assignee_name,
            epic_name = i.fields.customfield_10005 if hasattr(i.fields,'customfield_10005') else None,
            epic_link = i.fields.customfield_10008 if hasattr(i.fields,'customfield_10008') else None,
            parent = parent_id,
        ))
        # print("id: %i",i.id)
        # print('Type: %s',i.fields.issuetype.name)
        # print('Key: %s', i.key)
        # print('Summary: %s', i.fields.summary)
        # if hasattr(i.fields,'customfield_10026'):
        #     print('Customer: %s',i.fields.customfield_10026)
        # print('Status: %s', i.fields.status)
        # if hasattr(i.fields,'assignee'):
        #     print("Assignee: %s",i.fields.assignee)
        # if hasattr(i.fields,'customfield_10005'):
        #     print('Epic Name: %s',i.fields.customfield_10005)
        # if hasattr(i.fields,'customfield_10008'):
        #     print('Epic Link: %s',i.fields.customfield_10008)
        # if hasattr(i.fields,'parent'):
        #     print('Parent: %s',i.fields.parent)
        # print("Work Log:")
        worklogs = jira.worklogs(i.key)
        for w in worklogs:
            cleaned_worklogs.append(models.WorkLog(
                    id = w.id,
                    ticket_id = i.id,
                    epic_id = i.id,
                    name = w.raw['author']['displayName'],
                    started = parser.parse(w.raw['started']),
                    updated = parser.parse(w.raw['updated']),
                    time_spent = int(w.raw['timeSpentSeconds']),
                    work_des = w.raw['comment'] if 'comment' in w.raw else None
            ))
            # print("Entry:",iter)
            # print("    id :",w.id)
            # print("    name: %s",w.raw['author']['displayName'])
            # print("    started: %s",parser.parse(w.raw['started']))
            # print("    updated: %s",parser.parse(w.raw['updated']))
            # print("    time spent: %s",w.raw['timeSpentSeconds'])
            # print("    work description: %s",w.raw['comment'] if 'comment' in w.raw else None)
        #print("links: ",i.fields.issuelinks)


        # if len (i.fields.issuelinks) > 0 :
        #     for l in i.fields.issuelinks:
        #         print("    link:", l.raw))
        #print("timetracking: %s",str(cast(TimeTracking,i.fields.timetracking).raw))

        #print("________")
        children = jira.search_issues(f'parent={i.key}', maxResults=0)
        for c in children:
            print("Grabbing worklogs for child",c.key)
            worklogs = jira.worklogs(c.key)
            for w in worklogs:
                cleaned_worklogs.append(models.WorkLog(
                        id = w.id,
                        ticket_id = c.id,
                        epic_id = i.id,
                        name = w.raw['author']['displayName'],
                        started = parser.parse(w.raw['started']),
                        updated = parser.parse(w.raw['updated']),
                        time_spent = int(w.raw['timeSpentSeconds']),
                        work_des = w.raw['comment'] if 'comment' in w.raw else None
                ))
            
            # Subtasks
            subtasks = jira.search_issues(f'parent={c.key}', maxResults=0)
            for s in subtasks:
                print("    Grabbing worklogs for subtask",s.key)
                worklogs = jira.worklogs(s.key)
                for w in worklogs:
                    cleaned_worklogs.append(models.WorkLog(
                            id = w.id,
                            ticket_id = s.id,
                            epic_id = i.id,
                            name = w.raw['author']['displayName'],
                            started = parser.parse(w.raw['started']),
                            updated = parser.parse(w.raw['updated']),
                            time_spent = int(w.raw['timeSpentSeconds']),
                            work_des = w.raw['comment'] if 'comment' in w.raw else None
                    ))

    return cleaned_issues, cleaned_worklogs

