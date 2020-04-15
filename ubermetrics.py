# coding=utf-8
import os
import json
import api
import csv
import sys
import pickle
from tree import Tree

def try_connect(login, password):
    try:
        data = api.connect(login, password)
        return 'user_id=' + data['user_id']
    except Exception as ex:
        return str(ex)

def check_accounts(folder, isAPI):
    accounts = api.get_accounts(folder,  isAPI.lower() == 'true', True)
    for account in accounts:
        login_account = account[1][0]
        password_account = account[1][1]
        print('trying to connect to ' + login_account + ': ' + try_connect(login_account, password_account))

def print_accounts(folder, isAPI, isFlat):
    accounts = api.get_accounts(folder, isAPI.lower() == 'true', isFlat.lower() == 'true')
    for account in accounts:
        print(account)

def write_accounts(folder, isAPI):
    accounts = api.get_accounts(folder, isAPI.lower() == 'true', True)
    f = open('account.api2.csv', 'w+', encoding="utf-8")
    f.write('provider_name\tlogin\tpassword\n')
    for account in accounts:
        name = 'Ubermetrics-' + account[2].capitalize()
        login = account[1][0]
        password = account[1][1]
        f.write(name + '\t' + login + '\t' + password + '\n')
    f.close()

def build_config(login, password):
    data = {}
    try:
        data = api.connect(login, password)
        tree = api.get_search_tree({
            'user_id': data["user_id"], 
            'session_id': data["session_id"], 
            'auth_token': data["auth_tokens"].pop(),
        })
        
        items = tree['items']
        root = [x for x in items if x['name']=='#all'][0]
        
        return build_tree(root, items, login, password)

    except Exception as ex:
        print(login + '-' + password + ' -> error:' + str(ex))
        return None
        
def build_tree(node, items, login, password):
    if 'children' in node : 
        children = []
        for child in node['children']:
            id = child["_reference"]
            childNode = [x for x in items if x['name']==id][0]
            children.append(build_tree(childNode, items, login, password))
        return Tree(node, children, login, password)
    else:
        return Tree(node, None, login, password)

def write_node(node, f, str = ''):
    if str == '':
        str = '(' + node.login + ', ' + node.password + ')'
    else:
        str = str + ' -> ' + '(' + node.name + ', ' + node.type + ', ' + node.label + ')'
    f.write(str + '\n')
    if node.children is not None:
        for child in node.children:
            write_node(child, f, str)

def get_configs(folder, isAPI):
    accounts = api.get_accounts(folder, isAPI.lower() == 'true', True)
    root = Tree({"name":"root", "label":"root","type":"root"}, children=None)
    print('building configuration...')
    for account in accounts:
        login= account[1][0]
        password=account[1][1]
        print('--- get configuration for ' + login + '/' + password + '...')
        config = build_config(login, password)
        if config is not None:
            root.add_child(config)
    return root

def save_configs_to_csv(folder, isAPI):
    tree=get_configs (folder, isAPI)  
    
    print('saving configs to csv...')
    f = open('ubermetrics.csv', 'w+', encoding="utf-8")
    for child in tree.children:
        write_node(child, f)
    f.close()

def save_configs_to_cache(folder, isAPI):
    tree = get_configs(folder, isAPI)
    
    print('saving configs to cache...')
    afile = open(r'ubermetrics.pkl', 'wb')
    pickle.dump(tree, afile)
    afile.close()

def save_cache_to_csv():
    f = open(r'ubermetrics.pkl', 'rb')
    tree = pickle.load(f)
    f.close()

    print('saving cache to csv...')
    f = open('ubermetrics.csv', 'w+', encoding="utf-8")
    for child in tree.children:
        write_node(child, f)
    f.close()

try:
    if sys.argv[1] == '-cfg-to-cache':
        save_configs_to_cache(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == '-cfg-to-csv':
        save_configs_to_csv(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == '-cache-to-csv':
        save_cache_to_csv()
    elif sys.argv[1] == '-print':
        print_accounts(sys.argv[2], sys.argv[3], sys.argv[4])
    elif sys.argv[1] == '-check':
        check_accounts(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == '-write':
        write_accounts(sys.argv[2], sys.argv[3])
    else:
        raise Exception("action undefined: " + sys.argv[1]) 
except Exception as ex:
    print(ex)
    print("usage: python ubermetrics.py <action> <path_to_folder> <isAPI> [<isFlat>]")
    print("      actions :")
    print("          -cfg-to-csv : dump all Ubermetrics platform in ubermetrics.csv")
    print("          -cfg-to-cache : dump all Ubermtrics platform in ubermetrics.pkl")
    print("          -cache-to-csv : dump the cache in ubermetrics.csv")
    print("          -print : display all Ubermetrics accounts in the console")
    print("          -check : try to connect to all Ubermetrics accounts")
    print("          -write : dump all Ubermetrics accounts in account.api.csv")
    print("      path_to_folder : path to the JSON configuration files' folder")
    print("      isAPI : boolean. Use API account or customer account ?")
    print("      isFlat : boolean. Split France and Spain accounts or merge them into one FinalCustomer account ?")
    