import os
import sys
import json
import api
import commons
from functools import reduce

from tree import Tree

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

class Newsletter(object):
    def __init__(self, file_path, customer_id, customer_name):
        self.file_path = file_path
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.customer_name_normalized = commons.normalized(customer_name)

    def print(self):
        for k  in self.__dict__.keys():
            if k == 'feeds':
                print("feeds : [")
                for feed in self.__dict__[k]:
                    print(feed)
                print("]")
            else:
                print("{0} : {1}".format(k,self.__dict__[k]))
    
    def __repr__(self):
        feeds = " | ".join(map(lambda x:x['feed_id'], self.feeds))
        return self.file_path + " | " + self.customer_id + " | '" + self.customer_name + "' -> '" + self.newsletter_name +  "' [" + feeds + "]"

def extract_newsletter(filePath, idCustomer, nameCustomer, newsletters, values): 
    for (k, v) in newsletters.items():
        obj = Newsletter(filePath, idCustomer, nameCustomer)
        
        obj.newsletter_id = k
        obj.newsletter_name = commons.get_prop('newsletter_name', v)
        obj.subject = commons.get_prop('subject', v)
        obj.design_format = commons.get_prop('design_format', v)
        obj.design_title = commons.get_prop('design_title', v)
        obj.logoUrl = commons.get_prop('logoUrl', v)
        obj.primaryColor = commons.get_prop('primaryColor', v)
        obj.hour = commons.get_prop('hour', v)
        obj.min = commons.get_prop('min', v)
        obj.hour2 = commons.get_prop('hour2', v)
        obj.min2 = commons.get_prop('min2', v)
        obj.valuation_to_show = commons.get_prop('valuation_to_show', v)
        obj.order_by = commons.get_prop('order_by', v)
        obj.grouping = commons.get_prop('grouping', v)
        obj.num_mentions = commons.get_prop('num_mentions', v)
        obj.email_to = commons.get_prop('email_to', v)
        obj.email_remitent = commons.get_prop('email_remitent', v)
        obj.selection = commons.get_prop('selection', v)
        obj.name_remitent = commons.get_prop('name_remitent', v)
        obj.charset = commons.get_prop('charset', v)
        obj.type = commons.get_prop('type', v)
        obj.days = commons.join_prop('days', v, '|')

        if 'email_list_to' in v:
            obj.nb_list_to = str(len(v['email_list_to']))
            obj.email_list_to = commons.join_prop('email_list_to', v, ';')
        else:
            obj.nb_list_to = '0'
            obj.email_list_to = None
        
        if 'feeds' in v:
            obj.feeds=[]
            feeds = v['feeds']
            for (ke, va) in feeds.items():
                feedName = commons.get_prop('feedName', va)
                obj.feeds.append({
                    "feed_id" : ke,
                    "feed_name" : feedName,
                    "feed_name_normalized" : commons.normalized(feedName),
                    "valuation_to_show" : commons.get_prop('valuation_to_show', va),
                    "order_by" : commons.get_prop('order_by', va),
                    "selection" : commons.get_prop('selection', va),
                    "grouping" : commons.get_prop('grouping', va),
                    "num_mentions" : commons.get_prop('num_mentions', va)
                })

        values.append(obj)

def extract_all_newsletters(json_paths):
    values =[]

    for filePath in json_paths:
        with open(filePath) as json_file:
            try:
                data = json.load(json_file)
                #print('loading {}: OK'.format(filePath))
            except Exception as ex:
                #print('error loading {0}: {1}'.format(filePath, str(ex)))
                continue
            
            for item in data:
                if item is None: 
                    continue
                if 'module' in item:
                    module =item['module']
                    if 'newsletter' in module:
                        newsletters = module['newsletter']
                        nameCustomer = commons.get_prop('nameCustomer', item)
                        idCustomer = commons.get_prop('idCustomer', item)
                        extract_newsletter(filePath, idCustomer, nameCustomer, newsletters, values)
    
    return values

def save_newsletters(newsletters):
    values = []
    for newsletter in newsletters:
        if len(newsletter.feeds) > 0:
            for feed in newsletter.feeds:
                if feed['feed_id'] is None:
                    continue

                values.append((
                    newsletter.file_path,
                    newsletter.customer_id,
                    newsletter.customer_name,
                    newsletter.customer_name_normalized,
                    newsletter.newsletter_id,
                    newsletter.newsletter_name,
                    newsletter.subject,
                    newsletter.design_format,
                    newsletter.design_title,
                    newsletter.logoUrl,
                    newsletter.primaryColor,
                    newsletter.hour,
                    newsletter.min,
                    newsletter.hour2,
                    newsletter.min2,
                    newsletter.valuation_to_show,
                    newsletter.order_by,
                    newsletter.grouping,
                    newsletter.num_mentions,
                    newsletter.email_to,
                    newsletter.email_remitent,
                    newsletter.selection,
                    newsletter.name_remitent,
                    newsletter.charset,
                    newsletter.type,
                    newsletter.days,
                    newsletter.nb_list_to,
                    newsletter.email_list_to,
                    feed['feed_id'],
                    feed['valuation_to_show'],
                    feed['order_by'],
                    feed['selection'],
                    feed['grouping'],
                    feed['feed_name'],
                    feed['feed_name_normalized'],
                    feed['num_mentions']
                ))

    api.save_monitor_newsletters(values)

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
        newsletters = extract_all_newsletters(json_paths)
        save_newsletters(newsletters)
    else:
        raise Exception("action undefined: " + sys.argv[1])  

except Exception as ex:
    print(ex)
    print("usage: python refresh.py <action>")
    print("      actions :")
    print("          -ub :")
    print("          -aug :")
            


