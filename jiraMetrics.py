import sys
import getpass
from utils import ReleasedIn
from utils import NumberOfIssuesPerReleaseIn
from utils import MedianResolutionTimeIn
from utils import IssueTypeDistribution
from jira import JIRA

if len(sys.argv) < 5: # 1st arg is the metrics.py
    print("Arguments missing or in the wrong order:")
    print("    - Jira URL, e.g. https://myJiraServer.com")
    print("    - Jira Project short name, e.g. EXP")
    print("    - fixVersion, e.g. ReleaseV0.1")
    print("    - Match version string exact, e.g. 0 = false, 1 = True")
    print("    Jira Credentials, Optional:")
    print("        - Jira Username")
    print("        - Jira Password")
    sys.exit(1)

if len(sys.argv) > 5:
    user = sys.argv[5]
else:
    user = input("Jira username:")

if len(sys.argv) > 6:
    passwd = sys.argv[6]
else:
    passwd = getpass.getpass("Jira password for " + user + ":")

jira = JIRA(server=sys.argv[1], basic_auth=(user, passwd), validate=True)

project = sys.argv[2]
version = sys.argv[3]
exactMatch = False
if sys.argv[4].lower() in ['true', '1']:
    exactMatch = True

released = ReleasedIn(project, version, exactMatch, jira)
if not exactMatch:
    print("Number of Versions: " + str(len(released)))

issuesPerRelease = NumberOfIssuesPerReleaseIn(released, jira)
if not exactMatch:
    print("Number of Issues per Version:")
    i=0
    while i != len(released):
        print("    " + str(released[i]) + ": " + str(issuesPerRelease[i]))
        i+=1
else:
    print("Number of Issues " + str(released[0]) + ": " + str(issuesPerRelease[0]))

if not exactMatch:
    print("Median resolution time per Version:")
    i=0
    while i != len(released):
        medianResolutionTimePerPatch = MedianResolutionTimeIn(released[i], jira)
        print("    " + str(released[i]) + ": " + medianResolutionTimePerPatch)
        i+=1
else:
    medianResolutionTime = MedianResolutionTimeIn(released[0], jira)
    print("Median resolution time " + str(released[0]) + ": " + medianResolutionTime)

issueType = IssueTypeDistribution(released, jira)
print("Issue Type Distribution:")
print("    Bugs: " + str(issueType[0]) + "%")
print("    Epic: " + str(issueType[1]) + "%")
print("    Feature: " + str(issueType[2]) + "%")
print("    Task: " + str(issueType[3]) + "%")
print("    Sub-Task: " + str(issueType[4]) + "%")

sys.exit(0)