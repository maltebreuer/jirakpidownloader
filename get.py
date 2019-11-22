import numbers
import os
import json
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth

JIRA_USER = ""
JIRA_PASSWORD = ""

JIRA_VELOCITY_URL = ""
JIRA_BURNDOWN = ""
JIRA_SPRINTREPORT = ""
JIRA_ISSUETYPES = ""
JIRA_STATUS = ""
JIRA_SPRINTS = ""

JIRA_PROJECT_ISSUES = ""
JSON_OUT_DIRECTORY = ""

JSON_OUT_DIRECTORY = ""


def load_settings():
    global JIRA_USER
    global JIRA_PASSWORD

    global JIRA_VELOCITY_URL
    global JIRA_BURNDOWN
    global JIRA_SPRINTREPORT
    global JIRA_ISSUETYPES
    global JIRA_STATUS
    global JIRA_SPRINTS
    global JIRA_PROJECT_ISSUES
    global JSON_OUT_DIRECTORY

    # Load the environment variables from .env

    load_dotenv("auth.env")

    JIRA_USER = os.environ['JIRA_USER']
    JIRA_PASSWORD = os.environ['JIRA_PASSWORD']

    load_dotenv()

    # Import URLs relative to the base URL
    JIRA_VELOCITY_URL = os.environ['JIRA_BASE_URL'] + "/rest/greenhopper/latest/rapid/charts/velocity?rapidViewId=" + \
                        os.environ["RAPID_BOARD_ID"]
    JIRA_BURNDOWN = os.environ['JIRA_BASE_URL'] + "/rest/greenhopper/latest/rapid/charts/scopechangeburndownchart" \
                    + "?rapidViewId=" + os.environ["RAPID_BOARD_ID"] + "&sprintId="
    JIRA_SPRINTREPORT = os.environ['JIRA_BASE_URL'] + "/rest/greenhopper/latest/rapid/charts/sprintreport" \
                        + "?rapidViewId=" + os.environ["RAPID_BOARD_ID"] + "&sprintId="
    JIRA_ISSUETYPES = os.environ['JIRA_BASE_URL'] + "/rest/api/2/issuetype"
    JIRA_STATUS = os.environ['JIRA_BASE_URL'] + "/rest/api/2/status"
    JIRA_SPRINTS = os.environ['JIRA_BASE_URL'] + "/rest/agile/latest/board/" + os.environ['RAPID_BOARD_ID'] + "/sprint"
    JIRA_PROJECT_ISSUES = os.environ['JIRA_BASE_URL'] + "/rest/api/2/search?jql=project%3D" + os.environ['PROJECT_KEY'] \
                          + "&maxResults=1000&fields=id%2Ckey%2Cissuetype%2Cresolution%2Cresolutiondate%2Ccreator" \
                          + "%2Csubtasks%2Ccreated%2Creporter%2Cpriority%2Cupdated%2Cstatus%2Cparent%2CfixVersions" \
                          + "%2Ccustomfield_12405%2Ccustomfield_12406&expand=changelog"

    JSON_OUT_DIRECTORY = os.environ['JSON_OUT_DIRECTORY']


def cleanup():
    for root, dirs, files in os.walk(JSON_OUT_DIRECTORY):
        for file in files:
            os.remove(os.path.join(root, file))


def write_json_to_file(outFile, jsonObject):
    if not os.path.exists(JSON_OUT_DIRECTORY):
        os.makedirs(JSON_OUT_DIRECTORY)
    f = open(JSON_OUT_DIRECTORY + outFile, "w+")
    f.write(json.dumps(jsonObject, indent=4))


def get_data():
    print(os.environ['JIRA_BASE_URL'])

    print("Getting velocity...")
    r_velocity = requests.get(JIRA_VELOCITY_URL, auth=HTTPBasicAuth(JIRA_USER, JIRA_PASSWORD))
    write_json_to_file("velocity.json", r_velocity.json())
    print("Getting issue types...")
    r_issuetypes = requests.get(JIRA_ISSUETYPES, auth=HTTPBasicAuth(JIRA_USER, JIRA_PASSWORD))
    write_json_to_file("issuetypes.json", r_issuetypes.json())
    print("Getting status...")
    r_status = requests.get(JIRA_STATUS, auth=HTTPBasicAuth(JIRA_USER, JIRA_PASSWORD))
    write_json_to_file("status.json", r_status.json())
    print("Getting sprint data...")
    r_sprints = requests.get(JIRA_SPRINTS, auth=HTTPBasicAuth(JIRA_USER, JIRA_PASSWORD))
    write_json_to_file("sprints.json", r_sprints.json())
    print("Getting issue data...")
    r_issues = requests.get(JIRA_PROJECT_ISSUES, auth=HTTPBasicAuth(JIRA_USER, JIRA_PASSWORD))
    write_json_to_file("issues.json", r_issues.json())

    r_sprintreports = get_sprint_reports(r_sprints.json())
    write_json_to_file("sprintreports.json", r_sprintreports)

    r_burndowns = get_burndowns(r_sprints.json())
    r_velocity = get_velocity_from_burndowns(r_burndowns)


def get_sprint_reports(sprint_data):
    reports = {"data": []}
    print("Getting sprint reports...")
    for sprint in sprint_data["values"]:
        sprint_report = get_sprint_report(sprint["id"])
        sprint_report["sprint.id"] = sprint_report["sprint"]["id"]
        sprint_report.pop("sprint")
        reports["data"].append(sprint_report)
    return reports


def get_sprint_report(sprint_id):
    report = requests.get(JIRA_SPRINTREPORT + str(sprint_id), auth=HTTPBasicAuth(JIRA_USER, JIRA_PASSWORD))
    return report.json()


def get_burndowns(sprint_data):
    burndowns = {}
    print("Getting burndown data...")
    for sprint in sprint_data["values"]:
        burndowns[sprint["id"]] = get_burndown(sprint["id"])
    return burndowns


def get_burndown(sprint_id):
    burndown = requests.get(JIRA_BURNDOWN + str(sprint_id), auth=HTTPBasicAuth(JIRA_USER, JIRA_PASSWORD))
    burndown = burndown.json()
    burndown["sprint.id"] = sprint_id
    return burndown


def get_velocity_from_burndowns(burndowns):
    # TODO: WIP
    velocities = {"data": []}
    for sprint_id in burndowns:
        velocity = {"sprint.id": sprint_id}
        initial_estimate = get_initial_estimated_from_burndown(burndowns[sprint_id])
        velocities["data"].append(velocity)
    return velocities


def get_initial_estimated_from_burndown(burndown):
    # TODO: WIP
    issues_added_before_sprint_start = {}
    changes = burndown["changes"]
    sprint_start = burndown["startTime"]

    for time in changes:
        if int(time) <= sprint_start:
            for change in changes[time]:
                if change["key"] not in issues_added_before_sprint_start:
                    issues_added_before_sprint_start[change["key"]] = \
                        {"estimate":
                             {"time": None, "value": None},
                         "added":
                             {"time": None, "value": None},
                         "done":
                             {"time": None, "value": None}
                         }
                for changeType in change:
                    # The following change types have been observed:
                    #
                    # statC : Base statistic change. Seems to contain changes regarding estimation
                    # added : Issues has been added/removed from Sprint
                    # key   : Issue Key as seen in Jira
                    # column: Changes in the Sprint board column
                    if changeType == "statC":
                        if "newValue" in change["statC"]:
                            cur_time = issues_added_before_sprint_start[change["key"]]["estimate"]["time"]
                            if cur_time is None or int(time) > cur_time:
                                issues_added_before_sprint_start[change["key"]]["estimate"]["time"] = int(time)
                                issues_added_before_sprint_start[change["key"]]["estimate"]["value"] \
                                    = change["statC"]["newValue"]
                    elif changeType == "added":
                        cur_time = issues_added_before_sprint_start[change["key"]]["added"]["time"]
                        if cur_time is None or int(time) > cur_time:
                            issues_added_before_sprint_start[change["key"]]["added"]["time"] = int(time)
                            issues_added_before_sprint_start[change["key"]]["added"]["value"] \
                                = change["added"]
                    elif changeType == "key":
                        pass
                    elif changeType == "column":
                        # TODO: Still not exactly clear, how "done" should be handled
                        if "done" in change["column"]:
                            cur_time = issues_added_before_sprint_start[change["key"]]["done"]["time"]
                            if cur_time is None or int(time) > cur_time:
                                issues_added_before_sprint_start[change["key"]]["done"]["time"] = int(time)
                                issues_added_before_sprint_start[change["key"]]["done"]["value"] \
                                    = change["column"]["done"]
                        pass
                    else:
                        raise ValueError("Unhandled value: " + str(changeType))

    def filter_added(issue):
        return issue[1]["added"]["value"] is True and issue[1]["done"]["value"] is not True

    issues_added_before_sprint_start = dict(filter(filter_added, issues_added_before_sprint_start.items()))

    estimate_sum = 0
    for elem in issues_added_before_sprint_start.items():
        if isinstance(elem[1]["estimate"]["value"], numbers.Number):
            estimate_sum += elem[1]["estimate"]["value"]
    issues_added_before_sprint_start["estimateSum"] = estimate_sum

    print("Sprint " + str(burndown["sprint.id"]) + ": " + json.dumps(issues_added_before_sprint_start))
    return issues_added_before_sprint_start


print("""
     ██╗██╗██████╗  █████╗     ██╗  ██╗██████╗ ██╗
     ██║██║██╔══██╗██╔══██╗    ██║ ██╔╝██╔══██╗██║
     ██║██║██████╔╝███████║    █████╔╝ ██████╔╝██║
██   ██║██║██╔══██╗██╔══██║    ██╔═██╗ ██╔═══╝ ██║
╚█████╔╝██║██║  ██║██║  ██║    ██║  ██╗██║     ██║
 ╚════╝ ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝     ╚═╝
     _                     _                 _           
    | |                   | |               | |          
  __| | _____      ___ __ | | ___   __ _  __| | ___ _ __ 
 / _` |/ _ \ \ /\ / / '_ \| |/ _ \ / _` |/ _` |/ _ \ '__|
| (_| | (_) \ V  V /| | | | | (_) | (_| | (_| |  __/ |   
 \__,_|\___/ \_/\_/ |_| |_|_|\___/ \__,_|\__,_|\___|_|   
                                                         
                                            
                                                                                                                                            
""")

load_settings()
cleanup()
get_data()
