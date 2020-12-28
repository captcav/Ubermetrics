# coding=utf-8
import os
import json
import api
import csv
import sys
import pickle
from  matching import Tree
from dotenv import load_dotenv
load_dotenv()

def try_connect(login, password):
    try:
        data = api.connect(login, password)
        return 'user_id=' + data['user_id']
    except Exception as ex:
        return str(ex)

def check_active_accounts(isAPI:bool):
    accounts = api.get_ub_active_accounts(isAPI)
    for account in accounts:
        login = account[0]
        password = account[1]
        print('connect to ' + login + ': ' + try_connect(login, password))

def print_active_accounts(isAPI:bool):
    accounts = api.get_ub_active_accounts(isAPI)
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

def get_configs(isAPI:bool):
    print('building configuration...')

    accounts = api.get_ub_active_accounts(isAPI)
    root = Tree({"name":"root", "label":"root","type":"root"}, children=None)

    for account in accounts:
        login = account[0]
        password = account[1]
        print('--- get configuration for ' + login + '/' + password + '...')
        config = build_config(login, password)
        if config is not None:
            root.add_child(config)
    return root

def dump_configs(isAPI):
    print('dumping configs to csv...')

    tree=get_configs(isAPI)  
    f = open('./output/ubermetrics.csv', 'w+', encoding="utf-8")
    for child in tree.children:
        write_node(child, f)
    f.close()

try:
    action = sys.argv[1]
    isAPI = True
    if len(sys.argv) == 3:
        isAPI = sys.argv[2].lower() == 'true'

    if sys.argv[1] == '-print':
        print_active_accounts(isAPI)
    elif sys.argv[1] == '-check':
        check_active_accounts(isAPI)
    elif sys.argv[1] == '-dump':
        dump_configs(isAPI)
    else:
        raise Exception("action undefined: " + sys.argv[1]) 
except Exception as ex:
    print(ex)
    print("usage: python ubermetrics.py <action> [options]")
    print("   -print : display Ubermetrics accounts in the console")
    print("   -check [API accounts: True|False] : try to connect to Ubermetrics accounts")
    print("   -dump [API accounts: True|False] : dump Ubermetrics accounts configuration in ubermetrics.csv")    
    