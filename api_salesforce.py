import requests
import urllib.parse
import json
import os
from dotenv import load_dotenv
load_dotenv()

def get_sf_apps():
    endpoint = urllib.parse.urljoin(os.getenv("SALESFORCE_ENDPOINT"), 'api/V1/sf/apps') 
    apps = requests.get(endpoint)
    return apps.json()

def get_sf_app_by_name(name):
    endpoint = urllib.parse.urljoin(os.getenv("SALESFORCE_ENDPOINT"), 'api/V1/sf/apps') 
    endpoint = endpoint + '?name=' + name
    apps = requests.get(endpoint)
    return apps.json()
