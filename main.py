import os
import sys
import json
import api
import commons
from matching import do_matching, do_matching_from_file, Feed

def write_matchings_internal(monitor_file_path, ub_credentials, f):
    monitor_folder_name = commons.get_folder_name(monitor_file_path)
    feeds = do_matching(monitor_file_path, ub_credentials)
    for feed in feeds:
        f.write(monitor_folder_name + '\t' + str(feed) + '\n')

def write_matchings(configs, results_file_path:str='./output/matchings.all.csv'):
    if len(configs) == 1:
        monitor_folder_name = commons.get_folder_name(configs[0][0])
        results_file_path = './output/matchings.' + monitor_folder_name + '.csv'
    
    print('save to ' + results_file_path + '...')
    
    f = open(results_file_path, 'w+', encoding="utf-8")
    f.write('folder_name' + '\t' + 'json_file_path' + '\t' + 'json_customer_id' + '\t' + 'json_customer_name' + '\t' + 'json_customer_name_normalized' + '\t' + 'json_feed_id' + '\t' + 'json_feed_name' + '\t' + 'json_feed_name_normalized ' + '\t' + 'json_feed_property' + '\t' + 'json_feed_key' + '\t' + 'json_feed_format' + '\t' + 'json_feed_link' + '\t' + 'ub_login' + '\t' + 'ub_password' + '\t' + 'ub_name' + '\t' + 'ub_label' + '\t' + 'ub_type' + '\n')
    for config in configs:
        monitor_file_path = config[0]
        ub_credentials = config[1]
        write_matchings_internal(monitor_file_path, ub_credentials, f)
        print('----> saving results in ' + results_file_path + '...')
    f.close()

def write_accounts(configs, accounts_file_path:str='./output/ub.accounts.csv'):
    print('save to ' + accounts_file_path + '...')
    
    f = open(accounts_file_path, 'w+', encoding="utf-8")
    f.write('provider_name\tlogin\tpassword\tapp_url\tfolder_path\n')
    for config in configs:
        filepath = config[0]
        login = config[1][0] if config[1] is not None else '???'
        password = config[1][1] if config[1] is not None else '???'
        customer = config[2].capitalize()
        urls = config[3]
        url=urls[0] if urls is not None and len(urls) == 1 else '???'
        f.write(customer + '\t' + login + '\t' + password + '\t' + url + '\t' + filepath + '\n')
    f.close()

def write_augure_apps(apps_file_path:str='./output/augure.apps.csv'):
    apps = api.get_sf_applications()
    
    print('save to ' + apps_file_path + '...')
    f = open(apps_file_path, 'w+', encoding="utf-8")
    f.write('id\tname\turl\tfrontServer\tbackServer\tlanguage\taccount_name\taccount_tier\n')
    for app in apps:
        tier = app['account']['tier'] if app['account']['tier'] is not None else ''
        f.write(app['id'] + '\t' + app['name'] + '\t' + app['url'] + '\t' + app['frontServer'] + '\t' + app['backServer'] + '\t' + app['language'] + '\t' + app['account']['name'] + '\t' + tier + '\n')
    f.close()



try:
    action = sys.argv[1]
    isAPI = True
    working_folder = None
    if len(sys.argv) == 2:
        working_folder = os.getenv("MONITOR_WORKING_FOLDER")
    elif len(sys.argv) == 3:
        working_folder = sys.argv[2]

    if action == '-print-accounts':
        configs = api.process_all_accounts(working_folder, isAPI)
        for config in configs:
            print(config)
    elif action == '-write-accounts':
        configs = api.process_all_accounts(working_folder, isAPI)
        write_accounts(configs)
    elif action == '-write-augure-apps':
        write_augure_apps()
    elif action == '-match-all':
        configs = api.process_all_accounts(working_folder, isAPI)
        write_matchings(configs)
    elif action == '-match-one':
        configs = api.process_one_account(working_folder, isAPI)
        write_matchings(configs)
    else:
        raise Exception("action undefined: " + sys.argv[1])  
except Exception as ex:
    print(ex)
    print("usage: python matching.py <action> <path_to_folder> <isAPI>")
    print("      actions :")
    print("          -match : dump all matches between Monitor feeds to Ubermetrics searches in matchings.all.csv")
    print("          -write-accounts : write customer info in ub.accounts.csv")
    print("          -print-accounts : print customer info")
    print("          -write-augure-apps: write publisher apps info in augure.app.csv")
    print("      path_to_folder : path to the JSON configuration files' folder")
    print("      isAPI : boolean. Use API account or customer account ?")
            


