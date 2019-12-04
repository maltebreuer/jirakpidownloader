import os
import json

from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth

from burndown import Burndown

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

ENFORCE_SSL = True


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

    global ENFORCE_SSL

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

    if 'ENFORCE_SSL' in os.environ:
        ENFORCE_SSL = os.environ['ENFORCE_SSL'].lower() != "false"
    else:
        ENFORCE_SSL = True


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
    r_velocity = requests.get(JIRA_VELOCITY_URL, auth=HTTPBasicAuth(JIRA_USER, JIRA_PASSWORD), verify=ENFORCE_SSL)
    write_json_to_file("velocity.json", r_velocity.json())
    print("Getting issue types...")
    r_issuetypes = requests.get(JIRA_ISSUETYPES, auth=HTTPBasicAuth(JIRA_USER, JIRA_PASSWORD), verify=ENFORCE_SSL)
    write_json_to_file("issuetypes.json", r_issuetypes.json())
    print("Getting status...")
    r_status = requests.get(JIRA_STATUS, auth=HTTPBasicAuth(JIRA_USER, JIRA_PASSWORD), verify=ENFORCE_SSL)
    write_json_to_file("status.json", r_status.json())
    print("Getting sprint data...")
    r_sprints = requests.get(JIRA_SPRINTS, auth=HTTPBasicAuth(JIRA_USER, JIRA_PASSWORD), verify=ENFORCE_SSL)
    write_json_to_file("sprints.json", r_sprints.json())
    print("Getting issue data...")
    r_issues = requests.get(JIRA_PROJECT_ISSUES, auth=HTTPBasicAuth(JIRA_USER, JIRA_PASSWORD), verify=ENFORCE_SSL)
    write_json_to_file("issues.json", r_issues.json())

    r_sprintreports = get_sprint_reports(r_sprints.json())
    write_json_to_file("sprintreports.json", r_sprintreports)

    r_velocity_and_more = get_velocity_and_more(r_sprints)
    write_json_to_file("velocity-and-more.json", r_velocity_and_more)


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
    report = requests.get(JIRA_SPRINTREPORT + str(sprint_id), auth=HTTPBasicAuth(JIRA_USER, JIRA_PASSWORD),
                          verify=ENFORCE_SSL)
    return report.json()


def get_velocity_and_more(sprints):
    r_burndowns = get_burndowns(sprints.json())
    return get_velocity_and_more_from_burndowns(r_burndowns)


def get_burndowns(sprint_data):
    burndowns = {}
    print("Getting burndown data...")
    for sprint in sprint_data["values"]:
        burndowns[sprint["id"]] = get_burndown(sprint["id"])
    return burndowns


def get_burndown(sprint_id):
    burndown = requests.get(JIRA_BURNDOWN + str(sprint_id), auth=HTTPBasicAuth(JIRA_USER, JIRA_PASSWORD),
                            verify=ENFORCE_SSL)
    burndown = burndown.json()
    burndown["sprint.id"] = sprint_id
    return burndown


def get_velocity_and_more_from_burndowns(burndowns):
    velocities = {"data": []}
    for sprint_id in burndowns:
        data = extract_data_from_burndown(burndowns[sprint_id]).to_dictionary()
        velocity = {"sprint.id": sprint_id}
        for data_set in data.items():
            velocity[data_set[0]] = data_set[1]
        velocities["data"].append(velocity)
    return velocities


def extract_data_from_burndown(burndown_raw):
    changes = burndown_raw["changes"]
    sprint_start = burndown_raw["startTime"]
    if "completeTime" in burndown_raw:
        sprint_completed = burndown_raw["completeTime"]
    else:
        sprint_completed = burndown_raw["endTime"]

    burndown = Burndown(sprint_start, sprint_completed)

    for ch_time in changes:
        change_time = int(ch_time)
        for change in changes[ch_time]:
            issue_key = change["key"]
            if not burndown.has_issue(issue_key):
                burndown.add_issue(issue_key)
            curr_issue = burndown.get_issue(issue_key)
            for changeType in change:
                # The following change types have been observed:
                #
                # statC : Base statistic change. Seems to contain changes regarding estimation
                # added : Issues has been added/removed from Sprint
                # key   : Issue Key as seen in Jira
                # column: Changes in the Sprint board column
                if changeType == "statC":
                    if "newValue" in change["statC"]:
                        estimate = curr_issue.get_estimate()
                        stored_change_time_begin = estimate.get_at_beginning().get_time()
                        stored_change_time_completion = curr_issue.get_estimate().get_on_completion().get_time()
                        if change_time <= sprint_start:
                            if stored_change_time_begin is None or change_time > stored_change_time_begin:
                                estimate.get_at_beginning().set(change_time, change["statC"]["newValue"])
                        if stored_change_time_completion is None or change_time > stored_change_time_completion:
                            estimate.get_on_completion().set(change_time, change["statC"]["newValue"])
                elif changeType == "added":
                    added = curr_issue.get_added()
                    stored_change_time_begin = added.get_at_beginning().get_time()
                    stored_change_time_completion = added.get_on_completion().get_time()
                    if change_time <= sprint_start:
                        if stored_change_time_begin is None or change_time > stored_change_time_begin:
                            added.get_at_beginning().set(change_time, change["added"])
                    if stored_change_time_completion is None or change_time > stored_change_time_completion:
                        added.get_on_completion().set(change_time, change["added"])
                elif changeType == "key":
                    pass
                elif changeType == "column":
                    if "done" in change["column"]:
                        done = curr_issue.get_done()
                        stored_change_time_begin = done.get_at_beginning().get_time()
                        stored_change_time_completion = done.get_on_completion().get_time()
                        if change_time <= sprint_start:
                            if stored_change_time_begin is None or change_time > stored_change_time_begin:
                                done.get_at_beginning().set(change_time, change["column"]["done"])
                        if stored_change_time_completion is None or \
                                (stored_change_time_completion < change_time <= sprint_completed):
                            done.get_on_completion().set(change_time, change["column"]["done"])
                else:
                    raise ValueError("Unhandled value: " + str(changeType))

    def filter_added(issue):
        if issue[1].get_added().get_at_beginning().get_value() is not True:
            issue[1].get_added().get_at_beginning().reset()
        return issue

    def filter_completed(issue):
        if issue[1].get_done().get_on_completion().get_value() is not True:
            issue[1].get_done().get_on_completion().reset()
        return issue

    burndown.map(filter_added)
    burndown.map(filter_completed)
    burndown.calc()

    return burndown


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
