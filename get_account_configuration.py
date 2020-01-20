# coding=utf-8
import sys 
import os
import json
import urllib.parse
import urllib.request
import hashlib 

def request_api(params):
    url = 'https://api.ubermetrics-technologies.com'
    encoded_params = urllib.parse.urlencode(params)
    encoded_params = encoded_params.encode('ascii') # data should be bytes
    req = urllib.request.Request(url, encoded_params)
    #print('requesting ' + req.full_url + '?' + encoded_params.decode())
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())

if len(sys.argv) != 3: 
    print("usage: python export_ubermetrics_folders.py account_login account_password.")
    sys.exit()
    
account_login = sys.argv[1]
account_password = sys.argv[2]

login_request = request_api({'action' : 'login_request','user_name' : account_login})
if login_request['success'] != 'true':
    print (login_request['error'])
    sys.exit()

user_data = login_request['data']
user_id = user_data['user_id']
user_name_db = user_data['user_name_db']
user_seed = user_data['user_seed']
auth_seed = user_data['auth_seed']
md5Pass = hashlib.md5(account_password.encode())
md5WithUser = hashlib.md5((md5Pass.hexdigest() + user_seed).encode())
md5WithAuth = hashlib.md5((md5WithUser.hexdigest() + auth_seed).encode())

login = request_api({'action' : 'login', 'user_id' : user_id, 'pass' : md5WithAuth.hexdigest()})
if login['success'] != 'true':
    print (login['error'])
    sys.exit()

data = login['data']
session_id = data['session_id']
auth_tokens = data['auth_tokens']

get_searches = request_api({'action':'get_searches', 'user_id' : user_id, 'session_id' : session_id, 'auth_token' : auth_tokens.pop(), 'ipp' : 100})
if get_searches['success'] != 'true':
    print (get_searches['error'])
    sys.exit()

result = []
for search in get_searches['data']:
    line = []
    line.append(search['id']) 
    line.append(search['name'])
    line.append(search['folder'])
    result.append(line)

folders = map(lambda x : x[2], result)
folders = set(list(folders))
unique_folders = {}

for folder in folders:
    get_element = request_api({'action':'get_element', 'user_id' : user_id, 'session_id' : session_id, 'auth_token' : auth_tokens.pop(), 'element_id' : folder})
    if get_element['success'] == 'true':
        data = get_element['data']
        unique_folders[folder] = data['name']

f = open('files\\' + account_login + '.csv', 'w+', encoding="utf-8")
for item in result:
    f.write(str(item[0]) + '\t' + item[1] + '\t' + str(item[2]) + '\t' + unique_folders[item[2]] + '\t' + account_login + '\t' + account_password + '\n')

f.close()
