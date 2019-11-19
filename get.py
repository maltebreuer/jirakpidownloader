import os
import json
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth

# Load the environment variables from .env
load_dotenv()

# Import URLs relative to the base URL
JIRA_VELOCITY_URL = os.environ['JIRA_BASE_URL'] + "/rest/greenhopper/latest/rapid/charts/velocity?rapidViewId=" + os.environ["RAPID_BOARD_ID"]

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
r = requests.get(JIRA_VELOCITY_URL, auth=HTTPBasicAuth(os.environ['JIRA_USER'], os.environ['JIRA_PASSWORD']))

# Write velocity to file
f = open("out/velocity.json", "w+")
f.write(json.dumps(r.json(), indent=4))