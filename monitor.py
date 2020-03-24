# coding=utf-8
import sys 
import os
import csv
import json

def getJsonFilePaths(folder):   
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

def joinProps(property, obj, sep):
    if property in obj:
        values = obj[property]
        if values is None: 
            return ''
        else:
            return sep.join(values)
    else:
        return ''

def getProp(property, obj):
    if property in obj:
        value = obj[property]
        if value is None: 
            return ''
        else:
            return value
    else:
        return ''

def extract_properties(newsletter):
    line = getProp('design_format', newsletter)
    line += '\t' + getProp('design_title', newsletter)
    line += '\t' + getProp('hour', newsletter)
    line += '\t' + getProp('min', newsletter)
    line += '\t' + getProp('hour2', newsletter)
    line += '\t' + getProp('min2', newsletter)
    line += '\t' + getProp('valuation_to_show', newsletter)
    line += '\t' + getProp('order_by', newsletter)
    line += '\t' + getProp('grouping', newsletter)
    line += '\t' + getProp('num_mentions', newsletter)
    line += '\t' + getProp('email', newsletter)
    line += '\t' + getProp('selection', newsletter)
    line += '\t' + getProp('name_remitent', newsletter)
    line += '\t' + getProp('charset', newsletter)
    line += '\t' + getProp('type', newsletter)
    line += '\t' + joinProps('days', newsletter, '|')
    line += '\t' + joinProps('list', newsletter, '|')

    feeds = newsletter['feeds']
    result = ''
    for (k, v) in feeds.items():
        tmpLine = k   
        tmpLine += '\t' + getProp('valuation_to_show', v)
        tmpLine += '\t' + getProp('order_by', v)
        tmpLine += '\t' + getProp('selection', v)
        tmpLine += '\t' + getProp('grouping', v)                
        tmpLine += '\t' + getProp('feedName', v)                
        tmpLine += '\t' + getProp('num_mentions', v)
        result += line + '\t' + tmpLine + '\n'
    return result

def dump_newsletter(filePath, item, csv): 
    nameCustomer = ''
    if 'nameCustomer' in item: 
        nameCustomer = item['nameCustomer']
    
    if 'module' not in item:
        if debug == True:
            csv.write(filePath + '\t' + nameCustomer + '\t MODULE_NOT_FOUND \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \n')
        return 
    module = item['module']

    if 'newsletter' not in module:
        if debug == True:
            csv.write(filePath + '\t' + nameCustomer + '\t NEWSLETTER_NOT_FOUND \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \n')
        return 
    newsletters = module['newsletter']

    for (k, v) in newsletters.items():
        if 'feeds' not in v:
            if debug == True:
                csv.write(filePath + '\t' + nameCustomer + '\t' + k + '\t FEEDS_NOT_FOUND \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \n')
            return
        
        line = k 
        line += '\t' + getProp('design_format', v)
        line += '\t' + getProp('design_title', v)
        line += '\t' + getProp('hour', v)
        line += '\t' + getProp('min', v)
        line += '\t' + getProp('hour2', v)
        line += '\t' + getProp('min2', v)
        line += '\t' + getProp('valuation_to_show', v)
        line += '\t' + getProp('order_by', v)
        line += '\t' + getProp('grouping', v)
        line += '\t' + getProp('num_mentions', v)
        line += '\t' + getProp('email', v)
        line += '\t' + getProp('selection', v)
        line += '\t' + getProp('name_remitent', v)
        line += '\t' + getProp('charset', v)
        line += '\t' + getProp('type', v)
        line += '\t' + joinProps('days', v, '|')
        line += '\t' + joinProps('list', v, '|')
        
        feeds = v['feeds']
        for (ke, va) in feeds.items():
            feedLine = ke   
            feedLine += '\t' + getProp('valuation_to_show', va)
            feedLine += '\t' + getProp('order_by', va)
            feedLine += '\t' + getProp('selection', va)
            feedLine += '\t' + getProp('grouping', va)                
            feedLine += '\t' + getProp('feedName', va)                
            feedLine += '\t' + getProp('num_mentions', va)
        
            csv.write(filePath + '\t' + nameCustomer + '\t' + line + '\t' + feedLine + '\n')

def dump_newsletters(rootFolder, debug):
    json_paths = getJsonFilePaths(rootFolder)
    csv = open('monitor_newsletters.csv', 'w+', encoding="utf-8")
    csv.write('file_path \t name_customer \t newsletter_id \t newsletter_design_format \t newsletter_design_title \t newsletter_hour \t newsletter_min \t newsletter_hour2 \t newsletter_min2 \t newsletter_valuation_to_show \t newsletter_order_by \t newsletter_grouping \t newsletter_num_mentions \t newsletter_email \t newsletter_selection \t newsletter_name_remitent \t newsletter_charset \t newsletter_type \t newsletter_days \t newsletter_list \t feed_id \t feed_valuation_to_show \t feed_order_by \t feed_ selection \t feed_grouping \t feed_feedName \t feed_num_mentions \n')
    
    for filePath in json_paths:
        print('open ' + filePath + ' ...')
        with open(filePath) as json_file:
            data = json.load(json_file)
            if type(data) == list:
                for item in data:
                    dump_newsletter(filePath, item, csv)
            elif type(data) == dict:
                dump_newsletter(filePath, data, csv)
    csv.close()

def dump_feeds(rootFolder):
    json_paths = getJsonFilePaths(rootFolder)

    csv = open('monitor_feeds.csv', 'w+', encoding="utf-8")
    csv.write('filePath\tnameCustomer\t feed_id\tfeed_name\n')
    for filePath in json_paths:
        with open(filePath) as json_file:
            data = json.load(json_file)
            nameCustomer = ''
            for item in data: 
                if 'nameCustomer' in item: 
                    nameCustomer = item['nameCustomer']
                elif 'feedID' in item:
                    csv.write(filePath + '\t' + nameCustomer + '\t' + item['feedID'] + '\t' +  item['feedName'] + '\n')
    csv.close()

try:
    action = sys.argv[1]
    if action == 'newsletter':
        if len(sys.argv) >2:
            rootFolder = sys.argv[2]
            debug = False
            if len(sys.argv) == 4:
                debug = sys.argv[3] == '-d'
            dump_newsletters(rootFolder, debug)
        else:
            raise Exception("missing argument")
    elif action == 'feeds':
        if len(sys.argv) >2:
            rootFolder = sys.argv[2]
            dump_feeds(rootFolder)
        else:
            raise Exception("missing argument")

    else:
        raise Exception("action undefined: " + action) 
except Exception as ex:
    print(str(ex))
    print("usage: python monitor.py feeds")
    print("       python monitor.py newsletter <path_to_folder> [-d(ebug)]")




