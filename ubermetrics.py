# coding=utf-8
import json
import api
import csv
import sys
import pickle
from tree import Tree

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

def print_node(node, f, str = ''):
    if str == '':
        str = '(' + node.login + ', ' + node.password + ')'
    else:
        str = str + ' -> ' + '(' + node.name + ', ' + node.type + ', ' + node.label + ')'
    print(str)
    f.write(str + '\n')
    if node.children is not None:
        for child in node.children:
            print_node(child, f, str)

def dump_all(accounts_csv):
    root = Tree({"name":"root", "label":"root","type":"root"}, children=None)
    with open(accounts_csv, encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        print('building configuration...')
        for row in csv_reader:
            login=row[0]
            password=row[1]
            print('get configuration for ' + login + '/' + password + '...')
            config = build_config(login, password)
            if config is not None:
                root.add_child(config)
        print('done!')

    afile = open(r'ubermetrics.pkl', 'wb')
    pickle.dump(root, afile)
    afile.close()

def print_all():
    f = open(r'ubermetrics.pkl', 'rb')
    tree = pickle.load(f)
    f.close()

    f = open('ubermetrics.csv', 'w+', encoding="utf-8")
    for child in tree.children:
        print_node(child, f)
    f.close()

try:
    action = sys.argv[1]
    if action == '-d' or action == '-dump':
        dump_all('accounts.csv')
        print_all()
    elif action == '-p' or action == '-print':
        print_all()
    else:
        raise Exception("action undefined: " + action) 
except Exception as ex:
    print(ex)
    print("usage: python ubermetrics.py -d[ump]")
    print("       python ubermetrics.py -p[rint]")
