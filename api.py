# coding=utf-8
import json
import urllib.parse
import urllib.request
import hashlib
import os

def request_api(params):
    url = 'https://api.ubermetrics-technologies.com'
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

def get_accounts(folder, isAPI, isFlat): 
    accounts = []
    password_account = 'augure20'
    france_account = 'France-Augure-API' if isAPI else 'France-Augure'
    spain_account = 'Spain-Augure-API' if isAPI else 'Spain-Augure'
    for f in os.scandir(folder):
        if f.is_dir():
            filepath = os.path.join(folder, f.name)
            if isFlat:
                if f.name == 'finalCustomers':
                    accounts.append((filepath, (france_account, 'augure20'), 'France'))
                    accounts.append((filepath, (spain_account, 'augure20'), 'Spain'))
                else:
                    name_account = f.name.capitalize()
                    login_account = (name_account + '-Augure-API') if isAPI else name_account + '-Augure'
                    accounts.append((filepath, (login_account, password_account), f.name))
            else:
                if f.name == 'finalCustomers':
                    accounts.append((filepath, [(france_account, "augure20"), (spain_account,"augure20")], f.name))
                else:
                    name_account = f.name.capitalize()
                    login_account = (name_account + '-Augure-API') if isAPI else name_account + '-Augure'
                    accounts.append((filepath, (login_account,password_account), f.name))
        else:
            print(f.name + ' is not supported')

    return accounts

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

def get_augure_apps():
    url = 'http://localhost:5002/api/V1/sf/apps'
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())

def save_augure_apps_to_csv():
    print('requesting Salesforce...')
    apps = get_augure_apps()
    
    print('saving Augure apps to csv...')
    f = open('./output/augure.apps.csv', 'w+', encoding="utf-8")
    f.write('id\tname\turl\tfrontServer\tbackServer\tlanguage\taccount_name_\taccount_tier\n')
    for app in apps:
        f.write(app['id'] + '\t' + app['name'] + '\t' + app['url'] + '\t' + app['frontServer'] + '\t' + app['backServer'] + '\t' + app['language'] + '\t' + app['account']['name'] + '\t' + app['account']['tier'] + '\n')
    f.close()
