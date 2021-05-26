import statistics
from jira import JIRA
from jira.resources import Issue
from datetime import datetime
from datetime import timedelta

def GetVersion(project, version, exactMatch, jira):
    if not exactMatch:
        versions = jira.project_versions(project)
        allVersions = []
        i = 0
        while i != len(versions):
            if version in str(versions[i]) and versions[i].released:
                allVersions.append(versions[i])
            i += 1
        return allVersions

    return [jira.get_project_version_by_name(project, version)]

def ReleasedIn(project, version, exactMatch, jira):
    projectVersions = GetVersion(project, version, exactMatch, jira)
    versions = []
    i = 0
    while i != len(projectVersions):
        if projectVersions[i].released:
            versions.append(projectVersions[i])
        i += 1

    return versions
    

def NumberOfIssuesPerReleaseIn(patches, jira):
    issuesPerPatch = []

    i = 0
    while i != len(patches):
        query = "fixVersion=" + "'" + str(patches[i]) + "'"
        issues = jira.search_issues(query).total
        issuesPerPatch.append(issues)
        i += 1

    return issuesPerPatch

def MedianResolutionTimeIn(patch, jira):
    query = "fixVersion=" + "'" + str(patch) + "'"
    issues = jira.search_issues(query, maxResults=1000)

    minutes = []
    i = 0
    while i != len(issues):
        issue = jira.issue(issues[i])
        if str(issue.fields.resolution) == 'Done':
            createdTime = datetime.strptime(issue.fields.created.split(".")[0], '%Y-%m-%dT%H:%M:%S')
            resolvedTime = datetime.strptime(issue.fields.resolutiondate.split(".")[0], '%Y-%m-%dT%H:%M:%S')
            td_mins = int(round(abs((resolvedTime - createdTime).total_seconds()) / 60))
            minutes.append(td_mins)
        i += 1

    days = statistics.median(minutes) / 60 / 24
    hours = (days - int(days)) * 24
    minutes = (hours - int(hours)) * 60
    return str(int(days)) + 'd ' + str(int(hours)) + 'h ' + str(int(minutes)) + 'm'