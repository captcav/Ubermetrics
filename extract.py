# coding=utf-8
import sys 
import os
import csv
import api

def displayItem(id, parent, items, f):
    item = list(filter(lambda x: x["name"]==id, items))
    if len(item) != 1:
         raise Exception('Reference ' + str(id) + ' must be unique')
    item=item[0]

    result = parent + item['type'] + '[' + id + ']='  + item['label']
    f.write(result + '\n') 
    
    if item["type"] == "subfolder" or  item["type"] == "folder":
        for child in item["children"]:
            id = child["_reference"]
            displayItem(id, result + '->', items, f)
    elif item["type"] == "search":
        return
    else:
        raise Exception("type undefined: " + item["type"])

def displayAccountConfiguration(login, password, f):
    account_infos = login + '\t' + password + '\t'
    data = {}
    try:
        data = api.connect(login, password)
        tree = api.get_search_tree({
            'user_id': data["user_id"], 
            'session_id': data["session_id"], 
            'auth_token': data["auth_tokens"].pop(),
        })
        
        displayItem('#all', account_infos, tree['items'], f)

    except Exception as ex:
        f.write(account_infos + 'error:' + str(ex) + '\n')

accounts=[]

if len(sys.argv) == 2: 
    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print("file not found:" + filepath)
        sys.exit()

    with open(filepath, encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        for row in csv_reader:
            accounts.append({
                "login": row[0],
                "password": row[1]
            })
elif len(sys.argv) == 3:
        accounts.append({
            "login": sys.argv[1],
            "password": sys.argv[2]
    })
else:
    print("usage: python extract.py <accounts_file.csv>")
    print("       python extract.py <account_login> <account_password>")

f = open('ub_configurations.csv', 'w+', encoding="utf-8")

for account in accounts:
    print('get configuration for ' + account['login'] + ' | ' + account['password'] + '...')
    displayAccountConfiguration(account['login'], account['password'], f)

f.close()

