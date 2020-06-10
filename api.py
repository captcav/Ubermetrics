# coding=utf-8
import json
import urllib.parse
import urllib.request
import hashlib
import os
import unidecode
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

def get_ub_active_accounts():
    print('retrieve accounts list from Ubermetrics Google Sheet...')
    accounts = get_ubermetrics_accounts()

    tmp = list(map(lambda row:[row[0], row[1], os.getenv("UB_ACCOUNT_PASSWORD"), row[2]], accounts))
    tmp.append(['demoagency', 'demoagency', 'demo2020', 'in use'])
    tmp.append(['demofinal', 'demofinal', 'demo2020', 'in use'])

    return filter(lambda row:row[3] == 'in use', tmp)

def get_sf_applications():
    print('retrieve Publisher applications from Salesforce...')
    return api_salesforce.get_sf_apps()

def get_accounts_info(folder, isAPI): 
    ub_accounts = list(get_ub_active_accounts())
    sf_apps = get_sf_applications()
    
    results = []
    for f in os.scandir(folder):
        filepath = os.path.join(folder, f.name)

        # Get Application URL 
        application_url = []
        if f.name == 'marco':
            application_url.append("http://marcodecomunicacion.hosting.augure.com/Augure_MdCom")
        elif f.name == 'demo_agency':
            application_url.append('https://demo.hosting.augure.com/Demo_Agencia')
        elif f.name == 'certina' or f.name == 'rado' or f.name == 'swatch':
            application_url.append('http://mra.hosting.augure.com/Augure_MRA')   
        elif f.name == 'mayoral':
            application_url.append('http://ra.hosting.augure.com/Augure_RA')   
        elif f.name == 'elanedelman':
            application_url.append('http://agenceee.hosting.augure.com/Augure_EE')
        # elif f.name == 'mapfre':
        #     application_url.append("http://mapfre.hosting.augure.com/Augure_Mapfre")
        elif f.name != 'france' and f.name != 'spain':
            f1_name = f.name
            f1_name = unidecode.unidecode(f.name)

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

            if f.name in dict:
                f1_name = dict[f.name]

            arr =[]
            for app in sf_apps:
                if f1_name in app['name'] or f1_name in app['url'] or f1_name in app['account']['name']:  
                    arr.append(app['url'])
                elif app['name'].lower().find(f1_name,0) >= 0 or app['url'].lower().find(f1_name,0) >= 0 or app['account']['name'].lower().find(f1_name,0) >= 0:
                    arr.append(app['url'])

            application_url = arr

        # Get Ubermetrics info 
        ub_info = None
        if f.name == 'eliotrope':
            folder_name = 'eliotrop'
        elif f.name == 'demo_rp':
            folder_name = 'demofinal'
        elif f.name == 'demo_agency':
            folder_name = 'demoagency'
        elif f.name == 'interfacespain':
            folder_name = 'interface'
        else:
            folder_name = f.name

        for ub_account in ub_accounts:
            if ub_account[0].replace('-Augure','').lower() == folder_name.lower():
                ub_login = ub_account[1] if (isAPI.lower() == 'true') else ub_account[0]
                ub_password = ub_account[2]
                ub_info = (ub_login, ub_password)
                break
        
        results.append((filepath, ub_info, folder_name, application_url))
    
    return results

def get_JSON_filepaths(folder):   
    paths = [] 
    files_and_folders = [f for f in os.scandir(folder)]
    for f in files_and_folders:
        if f.is_dir():
            d = os.path.join(folder, f.name)
            filenames = os.listdir(d)
            for filename in filenames:
                paths.append(os.path.join(d, filename))
        else:
            paths.append(os.path.join(folder, f.name))
    
    return paths

def get_prop(property, obj):
    if property in obj:
        value = obj[property]
        if value is None: 
            return ''
        else:
            return value
    else:
        return ''

def join_prop(property, obj, sep):
    if property in obj:
        values = obj[property]
        if values is None: 
            return ''
        else:
            return sep.join(values)
    else:
        return ''

def normalized(s):
    if s is not None:
        s_diacritics_removed = unidecode.unidecode(s)
        return s_diacritics_removed.translate ({ord(c): "" for c in " '""!@#$%^&*()[]{};:,./<>?\\|`~-=_+"}).lower().capitalize()
    return s

def write_augure_apps():
    apps = get_sf_applications()
    
    print('save to augure.apps.csv...')
    f = open('./output/augure.apps.csv', 'w+', encoding="utf-8")
    f.write('id\tname\turl\tfrontServer\tbackServer\tlanguage\taccount_name_\taccount_tier\n')
    for app in apps:
        tier = app['account']['tier'] if app['account']['tier'] is not None else ''
        f.write(app['id'] + '\t' + app['name'] + '\t' + app['url'] + '\t' + app['frontServer'] + '\t' + app['backServer'] + '\t' + app['language'] + '\t' + app['account']['name'] + '\t' + tier + '\n')
    f.close()
