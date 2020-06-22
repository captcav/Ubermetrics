# coding=utf-8
import json
import urllib.parse
import urllib.request
import hashlib
import os
import unidecode
import commons
from api_google_sheet import get_ubermetrics_accounts
import api_salesforce
from dotenv import load_dotenv
load_dotenv()

def request_api(params):
    url = os.getenv("UB_API_ENDPOINT")
    encoded_params = urllib.parse.urlencode(params)
    encoded_params = encoded_params.encode('ascii') # data should be bytes
    req = urllib.request.Request(url, encoded_params)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())

def connect(login, password): 
    login_request = request_api({'action' : 'login_request','user_name' : login})
    if login_request['success'] != 'true':
        raise Exception(login_request['error']['message'])
        
    user_data = login_request['data']
    user_id = user_data['user_id']
    user_seed = user_data['user_seed']
    auth_seed = user_data['auth_seed']
    md5Pass = hashlib.md5(password.encode())
    md5WithUser = hashlib.md5((md5Pass.hexdigest() + user_seed).encode())
    md5WithAuth = hashlib.md5((md5WithUser.hexdigest() + auth_seed).encode())

    login = request_api({'action' : 'login', 'user_id' : user_id, 'pass' : md5WithAuth.hexdigest()})
    if login['success'] != 'true':
        raise Exception(login['error']['message'])
    
    data = login["data"]
    return {
        "user_id": user_id,
        "session_id": data['session_id'],
        "auth_tokens": data['auth_tokens']
    }

def get_search_tree(options):
    response = request_api({
        'action':'get_search_tree', 
        'user_id': options["user_id"], 
        'session_id': options["session_id"], 
        'auth_token': options["auth_token"],
        'marked':-1, 
        'sentiment': -1, 
        'read': -1, 
        'critical': -1, 
        't_max': '2012-12-01 00:00:00', 
        't_min': '2012-12-01 00:00:00',
        'language': '', 
        'group_type': ''
    })
    if response['success'] != 'true':
        raise Exception(response['error']['message'])
    
    tree = response["data"]
    return {
        "prop_label":tree['label'],
        "prop_identifier": tree['identifier'],
        "items": tree['items']
    }

def get_ub_active_accounts(isAPI:bool):
    print('retrieve accounts list from Ubermetrics Google Sheet...')
    ub_accounts = get_ubermetrics_accounts()

    accounts = []
    for row in ub_accounts:
        if len(row) == 3 and (row[2]=='in use' or row[2] == 'Account created'):
            accounts.append([row[1] if isAPI else row[0], os.getenv("UB_DEFAULT_PASSWORD"), row[2]])  
    accounts.append(['demoagency', 'demo2020', 'in use'])
    accounts.append(['demofinal', 'demo2020', 'in use'])

    return accounts 

def get_sf_applications():
    print('retrieve Publisher applications from Salesforce...')
    return api_salesforce.get_sf_apps()

def process_all_accounts(working_folder, isAPI): 
    ub_accounts = list(get_ub_active_accounts(isAPI))
    sf_apps = get_sf_applications()
    
    results = []
    for folder in os.scandir(working_folder):
        if not folder.is_dir:
            continue
        info = process_account(folder.name, folder.path, ub_accounts, sf_apps)
        results.append(info)
    return results

def process_one_account(folder_path:str, isAPI:bool = True):
    folder_name = commons.get_folder_name(folder_path)
    ub_accounts = list(get_ub_active_accounts(isAPI))
    sf_apps = get_sf_applications()
    
    results = []
    info = process_account(folder_name, folder_path, ub_accounts, sf_apps)
    results.append(info)
    return results

def process_account(folder_name:str, folder_path:str, ub_accounts:list, sf_apps:list):

        # guess Publisher application URL 
        application_url = []
        if folder_name == 'marco':
            application_url.append("http://marcodecomunicacion.hosting.augure.com/Augure_MdCom")
        elif folder_name == 'demo_agency':
            application_url.append('https://demo.hosting.augure.com/Demo_Agencia')
        elif folder_name == 'certina' or folder_name == 'rado' or folder_name == 'swatch':
            application_url.append('http://mra.hosting.augure.com/Augure_MRA')   
        elif folder_name == 'mayoral':
            application_url.append('http://ra.hosting.augure.com/Augure_RA')   
        elif folder_name == 'elanedelman':
            application_url.append('http://agenceee.hosting.augure.com/Augure_EE')
        elif folder_name == 'oxfaminternational':
            application_url.append('http://intermonoxfam.hosting.augure.com/Augure_IntermonOxfam')            
        # elif folder == 'mapfre':
        #     application_url.append("http://mapfre.hosting.augure.com/Augure_Mapfre")
        elif folder_name != 'france' and folder_name != 'spain':
            f1_name = folder_name
            f1_name = unidecode.unidecode(folder_name)

            dict = {
                "bursonmarstelleremea":"bmie",
                "elanedelman":"Elan Edelman",
                "spencerlewis":"Spencer & Lewis",
                "muséenature":"Musée de la Chasse et de la Nature",
                "interfacespain":"Interface Tourism Group",
                "gaiacomunicacion":"gaia",
                "frederiqueconstant":"Frederique Constant",
                "eolocomunicación":"eolo",
                "nintendo":"Nintendo SP",
                "lewis":"Lewis Communications SL"
            }

            if folder_name in dict:
                f1_name = dict[folder_name]

            arr =[]
            for app in sf_apps:
                if f1_name in app['name'] or f1_name in app['url'] or f1_name in app['account']['name']:  
                    arr.append(app['url'])
                elif app['name'].lower().find(f1_name,0) >= 0 or app['url'].lower().find(f1_name,0) >= 0 or app['account']['name'].lower().find(f1_name,0) >= 0:
                    arr.append(app['url'])

            application_url = arr
        
        # normalized JSON folder name 
        folder_normalized = folder_name
        if folder_name == 'eliotrope':
            folder_normalized = 'eliotrop'
        elif folder_name == 'demo_rp':
            folder_normalized = 'demofinal'
        elif folder_name == 'demo_agency':
            folder_normalized = 'demoagency'
        elif folder_name == 'interfacespain':
            folder_normalized = 'interface'
        elif folder_name == 'oxfaminternational':
            folder_normalized = 'oxfamiternational'

        # get Ubermetrics info 
        ub_info = None
        for ub_account in ub_accounts:
            if ub_account[0].replace('-Augure','').replace('-API', '').lower() == folder_normalized.lower():
                ub_info = (ub_account[0], ub_account[1])
                break
        
        return (folder_path, ub_info, folder_normalized, application_url)
