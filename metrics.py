import getpass
from utils import ReleasedIn
from utils import NumberOfIssuesPerReleaseIn
from utils import MedianResolutionTimeIn
from jira import JIRA

user = input("Username:")
passwd = getpass.getpass("Password for " + user + ":")

jira = JIRA(server="http://arashi:8080/jira", basic_auth=(user, passwd), validate=True)

project = "KIS"
version = "2020"
isPatch = True

released = ReleasedIn(project, version, isPatch, jira)
if isPatch:
    print("Number of Patches: " + str(len(released)))

issuesPerRelease = NumberOfIssuesPerReleaseIn(released, jira)
if isPatch:
    print("Number of Issues per Patch:")
    i=0
    while i != len(released):
        print("    " + str(released[i]) + ": " + str(issuesPerRelease[i]))
        i+=1
else:
    print("Number of Issues " + str(released[0]) + ": " + str(issuesPerRelease[0]))

if isPatch:
    print("Median resolution time per Patch:")
    i=0
    while i != len(released):
        medianResolutionTimePerPatch = MedianResolutionTimeIn(released[i], jira)
        print("    " + str(released[i]) + ": " + medianResolutionTimePerPatch)
        i+=1
else:
    medianResolutionTime = MedianResolutionTimeIn(released[0], jira)
    print("Median resolution time " + str(released[0]) + ": " + medianResolutionTime)
