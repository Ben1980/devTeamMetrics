import statistics
import enum
from jira import JIRA
from jira.resources import Issue
from datetime import datetime
from datetime import timedelta

def GetVersion(project, versionStr, exactMatch, jira):
    if not exactMatch:
        versions = jira.project_versions(project)
        allVersions = []

        for version in versions:
            if versionStr in str(version) and version.released:
                allVersions.append(version)
        return allVersions

    return [jira.get_project_version_by_name(project, versionStr)]

def ReleasedIn(project, version, exactMatch, jira):
    projectVersions = GetVersion(project, version, exactMatch, jira)
    versions = []

    for projectVersion in projectVersions:
        if projectVersion.released:
            versions.append(projectVersion)

    return versions
    

def NumberOfIssuesPerReleaseIn(versions, jira):
    issuesPerPatch = []

    for version in versions:
        query = "fixVersion=" + "'" + str(version) + "'"
        issues = jira.search_issues(query).total
        issuesPerPatch.append(issues)

    return issuesPerPatch

def MedianResolutionTimeIn(version, jira):
    query = "fixVersion=" + "'" + str(version) + "'"
    issues = jira.search_issues(query, maxResults=1000)
    minutes = []

    for issue in issues:
        isu = jira.issue(issue)
        if str(isu.fields.resolution) == 'Done':
            createdTime = datetime.strptime(isu.fields.created.split(".")[0], '%Y-%m-%dT%H:%M:%S')
            resolvedTime = datetime.strptime(isu.fields.resolutiondate.split(".")[0], '%Y-%m-%dT%H:%M:%S')
            td_mins = int(round(abs((resolvedTime - createdTime).total_seconds()) / 60))
            if td_mins > 0:
                minutes.append(td_mins)

    days = statistics.median(minutes) / 60 / 24
    hours = (days - int(days)) * 24
    minutes = (hours - int(hours)) * 60
    return str(int(days)) + 'd ' + str(int(hours)) + 'h ' + str(int(minutes)) + 'm'

class Type(enum.Enum):
    Bug = 0
    Epic = 1
    Feature = 2
    Task = 3
    SubTask = 4

    @classmethod
    def to_string(cls, type):
        if type == Type.Bug:
            return "Bug"
        if type == Type.Epic:
            return "Epic"
        if type == Type.Feature:
            return "New Feature"
        if type == Type.Task:
            return "Task"
        if type == Type.SubTask:
            return "Sub-task"


def IssueTypeDistribution(versions, jira):
    typeValues = []

    for type in Type:
        typeValues.append(AccumulateIssueType(type, versions, jira))

    return typeValues

def AccumulateIssueType(type: Type, versions, jira):
    typeResult = 0
    for version in versions:
        query = "fixVersion=" + "'" + str(version) + "' AND " + "issuetype=" + "'" + Type.to_string(type) + "'"
        issues = jira.search_issues(query, maxResults=1000)
        for issue in issues:
            typeResult += 1

    return typeResult


