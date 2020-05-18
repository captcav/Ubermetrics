import requests
import urllib.parse
import json

SALESFORCE_URL = 'http://localhost:5002'

def get_salesforce_apps():
    endpoint = urllib.parse.urljoin(SALESFORCE_URL, 'api/V1/sf/apps') 
    apps = requests.get(endpoint)
    return apps.json()
