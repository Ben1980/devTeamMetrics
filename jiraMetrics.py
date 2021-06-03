import sys
import getpass
from utils import ReleasedIn
from utils import NumberOfIssuesPerReleaseIn
from utils import MedianResolutionTimeIn
from utils import IssueTypeDistribution
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

released = ReleasedIn(project, version, exactMatch, jira)
if not exactMatch:
    print("Number of Versions: " + str(len(released)))

totalIssues = 0
issuesPerRelease = NumberOfIssuesPerReleaseIn(released, project, resolved, jira)
if not exactMatch:
    print("Number of Issues per Version:")
    for idx, issues in enumerate(issuesPerRelease):
        totalIssues += issues
        print("    " + str(released[idx]) + ": " + str(issues))
else:
    totalIssues += issuesPerRelease[0]
    print("Number of Issues " + str(released[0]) + ": " + str(issuesPerRelease[0]))

if not exactMatch:
    print("Median resolution time per Version:")
    for release in released:
        medianResolutionTimePerPatch = MedianResolutionTimeIn(release, project, resolved, jira)
        print("    " + str(release) + ": " + medianResolutionTimePerPatch)
else:
    medianResolutionTime = MedianResolutionTimeIn(released[0], project, resolved, jira)
    print("Median resolution time " + str(released[0]) + ": " + medianResolutionTime)

issueType = IssueTypeDistribution(released, project, resolved, jira)
print("Issue Type Distribution:")
print("    Bugs: " + "{:.2f}".format(100 * issueType[0]/totalIssues) + "%")
print("    Epic: " + "{:.2f}".format(100 * issueType[1]/totalIssues) + "%")
print("    Feature: " + "{:.2f}".format(100 * issueType[2]/totalIssues) + "%")
print("    Task: " + "{:.2f}".format(100 * issueType[3]/totalIssues) + "%")
print("    Sub-Task: " + "{:.2f}".format(100 * issueType[4]/totalIssues) + "%")

sys.exit(0)