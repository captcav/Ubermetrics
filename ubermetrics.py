# coding=utf-8
import os
import json
import api
import csv
import sys
import pickle
from tree import Tree
from dotenv import load_dotenv
load_dotenv()

def try_connect(login, password):
    try:
        data = api.connect(login, password)
        return 'user_id=' + data['user_id']
    except Exception as ex:
        return str(ex)

def check_active_accounts(isAPI):
    accounts = api.get_ub_active_accounts()
    for account in accounts:
        login = account[1] if (isAPI.lower() == 'true') else account[0]
        print('connect to ' + login + ': ' + try_connect(login, os.getenv("UB_ACCOUNT_PASSWORD")))

def print_active_accounts():
    accounts = api.get_ub_active_accounts()
    for account in accounts:
        print(account)

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

def get_configs(isAPI):
    print('building configuration...')

    accounts = api.get_ub_active_accounts()
    root = Tree({"name":"root", "label":"root","type":"root"}, children=None)
    for account in accounts:
        login = account[1] if (isAPI.lower() == 'true') else account[0]
        password = os.getenv("UB_ACCOUNT_PASSWORD")
        print('--- get configuration for ' + login + '/' + password + '...')
        config = build_config(login, password)
        if config is not None:
            root.add_child(config)
    return root

def dump_all_configs(isAPI):
    print('dumping configs to csv...')

    tree=get_configs (isAPI)  
    f = open('./output/ubermetrics.csv', 'w+', encoding="utf-8")
    for child in tree.children:
        write_node(child, f)
    f.close()

def save_configs_to_cache(isAPI):
    print('saving configs to cache...')
    
    tree = get_configs(isAPI)
    afile = open(r'ubermetrics.pkl', 'wb')
    pickle.dump(tree, afile)
    afile.close()

def save_cache_to_csv():
    f = open(r'ubermetrics.pkl', 'rb')
    tree = pickle.load(f)
    f.close()

    print('saving cache to csv...')
    f = open('./output/ubermetrics.csv', 'w+', encoding="utf-8")
    for child in tree.children:
        write_node(child, f)
    f.close()

try:
    if sys.argv[1] == '-dump-all':
        dump_all_configs(sys.argv[2])
    elif sys.argv[1] == '-cfg-to-cache':
        save_configs_to_cache(sys.argv[2])
    elif sys.argv[1] == '-cache-to-csv':
        save_cache_to_csv()
    elif sys.argv[1] == '-print':
        print_active_accounts()
    elif sys.argv[1] == '-check':
        check_active_accounts(sys.argv[2])
    else:
        raise Exception("action undefined: " + sys.argv[1]) 
except Exception as ex:
    print(ex)
    print("usage: python ubermetrics.py <action> <path_to_folder> <isAPI>")
    print("      actions :")
    print("          -cfg-to-csv : dump all Ubermetrics platform in ubermetrics.csv")
    print("          -cfg-to-cache : dump all Ubermtrics platform in ubermetrics.pkl")
    print("          -cache-to-csv : dump the cache in ubermetrics.csv")
    print("          -print : display all Ubermetrics accounts in the console")
    print("          -check : try to connect to all Ubermetrics accounts")
    print("      path_to_folder : path to the JSON configuration files' folder")
    print("      isAPI : boolean. Use API account or customer account ?")
    