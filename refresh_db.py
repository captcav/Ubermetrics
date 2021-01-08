import os
import sys
import json
import api
import commons
import matching

import importlib.util
spec = importlib.util.spec_from_file_location("googleFactory", "C:\\Work\\python\\commons\\google\\GoogleSheetServiceFactory.py")
googleFactory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(googleFactory)

def save_UM(configs):
    values = []
    for config in configs:
        filepath = config[0]
        login = config[1][0] if config[1] is not None else '???'
        password = config[1][1] if config[1] is not None else '???'
        customer = config[2].capitalize()
        urls = config[3]
        url=urls[0] if urls is not None and len(urls) == 1 else '???'
        values.append((customer, login, password, url, filepath))

    api.save_ub_accounts(values)

def save_augure_apps():
    apps = api.get_sf_applications()

    values = []
    for app in apps:
        tier = app['account']['tier'] if app['account']['tier'] is not None else ''
        values.append((app['id'], app['name'], app['url'], app['frontServer'], app['backServer'], app['language'], app['account']['name'], tier))

    api.save_augure_apps(values)

def save_factory_apps():
    feeds = api.get_factory_feeds()
    api.save_factory_feeds(feeds)

def extract_all_newsletters(json_paths):
    values =[]
    for file_path in json_paths:
        with open(file_path) as json_file:
            try:
                data = json.load(json_file)

                for item in data:
                    if item is None: 
                        continue
                   
                    customer_id = commons.get_prop('idCustomer', item)
                    customer_name = commons.get_prop('nameCustomer', item)
                    customer_name_normalized = commons.normalized(customer_name)
                    
                    if 'module' in item:
                        module =item['module']
                        if 'newsletter' in module:
                            counter = 0
                            newsletters = module['newsletter']
                            for (k, v) in newsletters.items():
                                if 'feeds' in v:
                                    counter += 1
                                    newsletter_id = k
                                    newsletter_name = commons.get_prop('newsletter_name', v)
                                    subject = commons.get_prop('subject', v)
                                    design_format = commons.get_prop('design_format', v)
                                    design_title = commons.get_prop('design_title', v)
                                    logoUrl = commons.get_prop('logoUrl', v)
                                    primaryColor = commons.get_prop('primaryColor', v)
                                    hour = commons.get_prop('hour', v)
                                    min1 = commons.get_prop('min', v)
                                    hour2 = commons.get_prop('hour2', v)
                                    min2 = commons.get_prop('min2', v)
                                    valuation_to_show = commons.get_prop('valuation_to_show', v)
                                    order_by = commons.join_prop('orderShowSearch', v, '|')
                                    grouping = commons.get_prop('grouping', v)
                                    num_mentions = commons.get_prop('num_mentions', v)
                                    email_to = commons.get_prop('email_to', v)
                                    email_remitent = commons.get_prop('email_remitent', v)
                                    selection = commons.get_prop('selection', v)
                                    name_remitent = commons.get_prop('name_remitent', v)
                                    charset = commons.get_prop('charset', v)
                                    newsletter_type = commons.get_prop('type', v)
                                    days = commons.join_prop('days', v, '|')

                                    if 'email_list_to' in v:
                                        nb_list_to = str(len(v['email_list_to']))
                                        email_list_to = commons.join_prop('email_list_to', v, ';')
                                    else:
                                        nb_list_to = '0'
                                        email_list_to = None

                                    feeds = v['feeds']
                                    for (ke, va) in feeds.items():
                                        feed_id = ke
                                        feed_name = commons.get_prop('feedName', va)
                                        feed_name_normalized = commons.normalized(feed_name)
                                        feed_valuation_to_show = commons.get_prop('valuation_to_show', va)
                                        feed_order_by = commons.get_prop('order_by', va)
                                        feed_selection = commons.get_prop('selection', va)
                                        feed_grouping = commons.get_prop('grouping', va)
                                        feed_num_mentions = commons.get_prop('num_mentions', va)

                                        values.append((
                                            file_path, 
                                            customer_id,
                                            customer_name,
                                            customer_name_normalized,
                                            newsletter_id,
                                            newsletter_name,
                                            subject,
                                            design_format,
                                            design_title,
                                            logoUrl,
                                            primaryColor,
                                            hour,
                                            min1,
                                            hour2,
                                            min2,
                                            valuation_to_show,
                                            order_by,
                                            grouping,
                                            num_mentions,
                                            email_to,
                                            email_remitent,
                                            selection,
                                            name_remitent,
                                            charset,
                                            newsletter_type,
                                            days,
                                            nb_list_to,
                                            email_list_to,
                                            feed_id,
                                            feed_valuation_to_show,
                                            feed_order_by,
                                            feed_selection,
                                            feed_grouping,
                                            feed_name,
                                            feed_name_normalized,
                                            feed_num_mentions
                                        ))
                            print('extracting {0} newsletters from {1}: OK'.format(counter, file_path))
            except Exception as ex:
                print('ERROR extracting newsletters from {0}: {1}'.format(file_path, str(ex)))
    return values

def save_matchings(configs):
    feeds = []
    for config in configs:
        monitor_file_path = config[0]
        ub_credentials = config[1]
        matches = matching.do_matching(monitor_file_path, ub_credentials)
        feeds.extend(matches)
    data = []
    for feed in feeds:
        data.append(feed.toTuple())
    
    api.save_all_matchings(data)

def save_matchings_from_file(ub_login, ub_password, file_path):
    data = commons.extract_csv_to_tuples(file_path, ";")
    feeds = []
    for row in data[1:]:
        feed = matching.Feed(None, None, row[2] + row[3], None, row[4])
        feed.ub_login = ub_login
        feed.ub_password = ub_password
        feeds.append(feed)

    data = []
    matching.do_matching_from_file(ub_login, ub_password, feeds)
    for feed in filter(lambda x:x.ub_name is not None, feeds):
        data.append(feed.toTuple())
    
    return data
        
try:
    action = sys.argv[1]
    if action == '-ub':
        working_folder = sys.argv[2]
        configs = api.process_all_accounts(working_folder, True)
        save_UM(configs)
    elif action == '-aug':
        save_augure_apps()
    elif action == '-fac':
        save_factory_apps()
    elif action == '-news':
        working_folder = sys.argv[2]
        json_paths = commons.get_json_filepath(working_folder)
        result = extract_all_newsletters(json_paths)
        api.save_monitor_newsletters(result)
    elif action == '-uberfac':
       api.save_uberfactory_feeds()
    elif action == '-match':
        working_folder = sys.argv[2]
        configs = api.process_all_accounts(working_folder, True)
        save_matchings(configs)
    elif action == '-match-file':
        ub_login = sys.argv[2]
        ub_password = sys.argv[3] 
        file_path = sys.argv[4] 
        data = save_matchings_from_file(ub_login, ub_password, file_path)
        api.save_all_matchings(data)
    elif action == '-match-norm':
        api.save_matchings_normalized()
    elif action == '-google':
        api.export_to_google()
    else:
        raise Exception("action undefined: " + sys.argv[1])  

except Exception as ex:
    print(ex)
    print("usage: python refresh.py -<ub|aug|fac|news>")
            