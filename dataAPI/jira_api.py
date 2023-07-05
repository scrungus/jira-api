import json
from jira import JIRA
from jira.client import ResultList
from jira.resources import Issue, TimeTracking
from typing import cast
from dateutil import parser
from datetime import timedelta
import dataAPI.models as models
import logging

def fetch_jira_data(project):

    file = "config.json"
    config = json.load(open(file))

    jira = JIRA(
        options={'server': config['url']},
        basic_auth=(config['user'], config['password'])
    )

    # fields = jira.fields()
    # for f in fields:
    #   if "Epic" or "Customer" or "Work" in f['name']:
    #     logging.info(f)

    def get_all_issues(jira_client, project_name, fields):
        issues = []
        i = 0
        chunk_size = 100
        while True:
            chunk = jira_client.search_issues(f'project={project_name}', startAt=i, maxResults=chunk_size)
            i += chunk_size
            issues += chunk.iterable
            if i >= chunk.total:
                break
        return issues

    issues = cast(ResultList[Issue], get_all_issues(jira, project, ["id", "fixVersion"]))
    cleaned_issues = []
    cleaned_worklogs = []

    for i in issues: 

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
            issuetype = i.fields.issuetype.name,
            summary = i.fields.summary,
            status = i.fields.status.name,
            customer = i.fields.customfield_10026 if hasattr(i.fields,'customfield_10026') else None,
            assignee = assignee_name,
            epic_name = i.fields.customfield_10005 if hasattr(i.fields,'customfield_10005') else None,
            epic_link = i.fields.customfield_10008 if hasattr(i.fields,'customfield_10008') else None,
            parent = parent_id,
        ))
        logging.info("id:",i.id)
        logging.info('Type:',i.fields.issuetype.name)
        logging.info('Key:', i.key)
        logging.info('Summary:', i.fields.summary)
        if hasattr(i.fields,'customfield_10026'):
            logging.info('Customer:',i.fields.customfield_10026)
        logging.info('Status:', i.fields.status)
        if hasattr(i.fields,'assignee'):
            logging.info("Assignee:",i.fields.assignee)
        if hasattr(i.fields,'customfield_10005'):
            logging.info('Epic Name:',i.fields.customfield_10005)
        if hasattr(i.fields,'customfield_10008'):
            logging.info('Epic Link:',i.fields.customfield_10008)
        if hasattr(i.fields,'parent'):
            logging.info('Parent:',i.fields.parent)
        logging.info("Work Log:")
        for iter,w in enumerate(i.fields.worklog.worklogs):
            cleaned_worklogs.append(models.WorkLog(
                    ticket_id = i.id,
                    name = w.raw['author']['displayName'],
                    started = parser.parse(w.raw['started']),
                    time_spent = timedelta(seconds=int(w.raw['timeSpentSeconds'])),
                    work_des = w.raw['comment']
            ))
            logging.info("Entry:",iter)
            logging.info("    name:",w.raw['author']['displayName'])
            logging.info("    started:",parser.parse(w.raw['started']))
            logging.info("    time spent:",w.raw['timeSpentSeconds'])
            logging.info("    work description:",w.raw['comment'])
        #logging.info("links: ",i.fields.issuelinks)

        # if len (i.fields.issuelinks) > 0 :
        #     for l in i.fields.issuelinks:
        #         logging.info("    link:", l.raw))
        logging.info("timetracking: ",cast(TimeTracking,i.fields.timetracking).raw)

        logging.info("________")

    return cleaned_issues, cleaned_worklogs


# cleaned_issues, cleaned_worklogs = fetch_jira_data('\'Platforms Team\'')

# for i in cleaned_issues:
#     print(i.__dict__)

# from jiraone import LOGIN, issue_export, endpoint
# import json
# import datetime

# LOGIN(**config)

# jql = "project in ('Platforms Team') order by created DESC"
# issue_export(jql=jql,final_file=f'export-{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

# #jql = "project in ('Platforms Team') order by created DESC"