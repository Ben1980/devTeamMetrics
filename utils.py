import statistics
import enum
from datetime import datetime

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
    
def NumberOfIssuesPerReleaseIn(versions, project, resolved, jira):
    issuesPerPatch = []

    for version in versions:
        query = Query(resolved, str(project), str(version))
        issues = jira.search_issues(query).total
        issuesPerPatch.append(issues)

    return issuesPerPatch

def MedianResolutionTimeIn(version, project, resolved, jira):
    query = Query(resolved, str(project), str(version))
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


def IssueTypeDistribution(versions, project, resolved, jira):
    typeValues = []

    for type in Type:
        typeValues.append(AccumulateIssueType(type, versions, project, resolved, jira))

    return typeValues

def AccumulateIssueType(type: Type, versions, project, resolved, jira):
    typeResult = 0
    for version in versions:
        query = Query(resolved, str(project), str(version), Type.to_string(type))

        issues = jira.search_issues(query, maxResults=1000)
        for issue in issues:
            typeResult += 1

    return typeResult

def Query(resolved, project = "", version = "", type = ""):
    query = ""

    if len(project) > 0:
        query += "project=" + project

    if len(version) > 0:
        if len(query) > 0:
            query += " AND "
        query += "fixVersion=" + "'" + version + "'"

    if len(type) > 0:
        if len(query) > 0:
            query += " AND "
        query += "issuetype=" + "'" + type + "'"

    if resolved:
        if len(query) > 0:
            query += " AND "
        query += "resolution=Done"

    return query
