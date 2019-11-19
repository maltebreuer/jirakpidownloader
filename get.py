import os
import json
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth

def writeJsonToFile(outFile, jsonObject):
     f = open("out/" + outFile, "w+")
     f.write(json.dumps(jsonObject, indent=4))

# Load the environment variables from .env
load_dotenv()

# Import URLs relative to the base URL
JIRA_VELOCITY_URL = os.environ['JIRA_BASE_URL'] + "/rest/greenhopper/latest/rapid/charts/velocity?rapidViewId=" + os.environ["RAPID_BOARD_ID"]
JIRA_ISSUETYPES = os.environ['JIRA_BASE_URL'] + "/rest/api/2/issuetype"
JIRA_STATUS = os.environ['JIRA_BASE_URL'] + "/rest/api/2/status"
JIRA_SPRINTS = os.environ['JIRA_BASE_URL'] + "/rest/agile/latest/board/" + os.environ['RAPID_BOARD_ID'] + "/sprint"
JIRA_PROJECT_ISSUES = os.environ['JIRA_BASE_URL'] + "/rest/api/2/search?jql=project%3D" + os.environ['PROJECT_KEY'] + "&maxResults=1000&fields=id%2Ckey%2Cissuetype%2Cresolution%2Cresolutiondate%2Ccreator%2Csubtasks%2Ccreated%2Creporter%2Cpriority%2Cupdated%2Cstatus%2Cparent%2CfixVersions%2Ccustomfield_12405%2Ccustomfield_12406&expand=changelog"

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
print(os.environ['JIRA_BASE_URL'])

print("Getting velocity...")
r_velocity = requests.get(JIRA_VELOCITY_URL, auth=HTTPBasicAuth(os.environ['JIRA_USER'], os.environ['JIRA_PASSWORD']))
writeJsonToFile("velocity.json", r_velocity.json())
print("Getting issue types...")
r_issuetypes = requests.get(JIRA_ISSUETYPES, auth=HTTPBasicAuth(os.environ['JIRA_USER'], os.environ['JIRA_PASSWORD']))
writeJsonToFile("issuetypes.json", r_issuetypes.json())
print("Getting status...")
r_status = requests.get(JIRA_STATUS, auth=HTTPBasicAuth(os.environ['JIRA_USER'], os.environ['JIRA_PASSWORD']))
writeJsonToFile("status.json", r_status.json())
print("Getting sprint data...")
r_sprints = requests.get(JIRA_SPRINTS, auth=HTTPBasicAuth(os.environ['JIRA_USER'], os.environ['JIRA_PASSWORD']))
writeJsonToFile("sprints.json", r_sprints.json())
print("Getting issue data...")
r_issues = requests.get(JIRA_PROJECT_ISSUES, auth=HTTPBasicAuth(os.environ['JIRA_USER'], os.environ['JIRA_PASSWORD']))
writeJsonToFile("issues.json", r_issues.json())