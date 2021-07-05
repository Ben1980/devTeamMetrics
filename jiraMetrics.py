import sys
import getpass
from utils import Query
from utils import Versions
from utils import NumberOfIssuesPerReleaseIn
from utils import MedianResolutionTimeIn
from utils import IssueTypeDistribution
from datetime import datetime
from collections import OrderedDict
from jira import JIRA

if len(sys.argv) < 6: # 1st arg is the metrics.py
    print("Arguments missing or in the wrong order:")
    print("    - Jira URL, e.g. https://myJiraServer.com")
    print("    - Jira Project short name, e.g. EXP")
    print("    - fixVersion, e.g. ReleaseV0.1")
    print("    - Match version string exact")
    print("    - Search only resolved issues")
    print("    Jira Credentials, Optional:")
    print("        - Jira Username")
    print("        - Jira Password")
    sys.exit(1)

if len(sys.argv) > 6:
    user = sys.argv[6]
else:
    user = input("Jira username:")

if len(sys.argv) > 7:
    passwd = sys.argv[7]
else:
    passwd = getpass.getpass("Jira password for " + user + ":")

jira = JIRA(server=sys.argv[1], basic_auth=(user, passwd), validate=True)

project = sys.argv[2]
version = sys.argv[3]
exactMatch = False
if sys.argv[4].lower() in ['true', '1']:
    exactMatch = True

resolved = False
if sys.argv[5].lower() in ['true', '1']:
    resolved = True

versions = Versions(project, version, exactMatch, jira)
if not exactMatch:
    print("Number of Versions: " + str(len(versions)))

totalIssues = 0
issuesPerRelease = NumberOfIssuesPerReleaseIn(versions, project, "", resolved, False, jira)
if not exactMatch:
    print("Number of Issues per Version:")
    for idx, issues in enumerate(issuesPerRelease):
        totalIssues += issues
        print("    " + str(versions[idx]) + ": " + str(issues))
else:
    totalIssues += issuesPerRelease[0]
    print("Number of Issues " + str(versions[0]) + ": " + str(issuesPerRelease[0]))

if not exactMatch:
    print("Median resolution time per Version:")
    for release in versions:
        medianResolutionTimePerPatch = MedianResolutionTimeIn(release, project, resolved, jira)
        print("    " + str(release) + ": " + medianResolutionTimePerPatch)
else:
    medianResolutionTime = MedianResolutionTimeIn(versions[0], project, resolved, jira)
    print("Median resolution time " + str(versions[0]) + ": " + medianResolutionTime)

issueType = IssueTypeDistribution(versions, project, resolved, jira)
print("Issue Type Distribution:")
print("    Bugs: " + "{:.2f}".format(100 * issueType[0]/totalIssues) + "%")
print("    Epic: " + "{:.2f}".format(100 * issueType[1]/totalIssues) + "%")
print("    Feature: " + "{:.2f}".format(100 * issueType[2]/totalIssues) + "%")
print("    Task: " + "{:.2f}".format(100 * issueType[3]/totalIssues) + "%")
print("    Sub-Task: " + "{:.2f}".format(100 * issueType[4]/totalIssues) + "%")

year = "2021"
numberOfIssues = NumberOfIssuesPerReleaseIn("", project, year, False, False, jira)
numberOfResolvedIssues = NumberOfIssuesPerReleaseIn("", project, year, True, True, jira)
rejected = Versions(project, "Rejected", exactMatch, jira)
numberOfRejectedIssues = NumberOfIssuesPerReleaseIn(rejected, project, year, False, True, jira)
totalIssues = 0
for issues in numberOfIssues:
    totalIssues += issues
totalResolvedIssues = 0
for issues in numberOfResolvedIssues:
    totalResolvedIssues += issues
totalRejectedIssues = 0
for issues in numberOfRejectedIssues:
    totalRejectedIssues += issues
print("Number Of Issues " + year + ": " + str(totalIssues) + "/" + str(totalResolvedIssues) + "/" + str(totalRejectedIssues) + " issues/resolved/rejected")

distribution = {}
for version in versions:
    query = Query(False, str(project), str(version), "Bug")
    issues = jira.search_issues(query, maxResults=10000)
    for issue in issues:
        date = datetime.fromisoformat(issue.fields.created.split("T")[0])
        quarter = (date.month-1)//3 + 1
        if not date.year in distribution.keys():
            distribution[date.year] = {}
        if not quarter in distribution[date.year]:
            distribution[date.year][quarter] = 0
        distribution[date.year][quarter]  += 1

for key in sorted(distribution.keys()):
    print(str(key) + ":")
    for qar in sorted(distribution[key].keys()):
        print(str(qar) + ":" + str(distribution[key][qar]))



sys.exit(0)