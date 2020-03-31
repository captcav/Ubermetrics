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

def dump_newsletter(filePath, idCustomer, nameCustomer, newsletters, csv, csv_inactive): 
    for (k, v) in newsletters.items():
        line = k 
        line += '\t' + getProp('design_format', v)
        line += '\t' + getProp('design_title', v)
        line += '\t' + getProp('logoUrl', v)
        line += '\t' + getProp('primaryColor', v)
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
        if 'list' in v:
            line += '\t' + str(len(v['list']))
        else:
            line += '\t'
        line += '\t' + joinProps('list', v, ';')

        if 'feeds' not in v:
            csv_inactive.write(filePath + '\t' + idCustomer + '\t' + nameCustomer + '\t' + line + '\t FEED_NOT_FOUND' + '\n')
        else:
            feeds = v['feeds']
            for (ke, va) in feeds.items():
                feedLine = ke   
                feedLine += '\t' + getProp('valuation_to_show', va)
                feedLine += '\t' + getProp('order_by', va)
                feedLine += '\t' + getProp('selection', va)
                feedLine += '\t' + getProp('grouping', va)                
                feedLine += '\t' + getProp('feedName', va)                
                feedLine += '\t' + getProp('num_mentions', va)
                csv.write(filePath + '\t' + idCustomer + '\t' + nameCustomer + '\t' + line + '\t' + feedLine + '\n')

def dump_newsletters(rootFolder):
    json_paths = getJsonFilePaths(rootFolder)
    
    default_headers = 'file_path \t idCustomer \t name_customer \t newsletter_id \t newsletter_design_format \t newsletter_design_title \t logo_url \t primary_color \t newsletter_hour \t newsletter_min \t newsletter_hour2 \t newsletter_min2 \t newsletter_valuation_to_show \t newsletter_order_by \t newsletter_grouping \t newsletter_num_mentions \t newsletter_email \t newsletter_selection \t newsletter_name_remitent \t newsletter_charset \t newsletter_type \t newsletter_days \t newsletter_nb_list \t newsletter_list'
    csv = open('json_newsletters.csv', 'w+', encoding="utf-8")
    csv.write(default_headers + '\t feed_id \t feed_valuation_to_show \t feed_order_by \t feed_ selection \t feed_grouping \t feed_feedName \t feed_num_mentions \n')
    csv_inactive = open('json_newsletters_inactive.csv', 'w+', encoding="utf-8")
    csv_inactive.write(default_headers + '\t msg \n')

    for filePath in json_paths:
        with open(filePath) as json_file:
            data = json.load(json_file)
            for item in data:
                if 'module' in item:
                    module =item['module']
                    if 'newsletter' in module:
                        newsletters = module['newsletter']
                        nameCustomer = getProp('nameCustomer', item)
                        idCustomer = getProp('idCustomer', item)
                        dump_newsletter(filePath,idCustomer, nameCustomer, newsletters, csv, csv_inactive)
    csv.close()

def dump_feeds(rootFolder):
    json_paths = getJsonFilePaths(rootFolder)
    
    csv = open('json_feeds.csv', 'w+', encoding="utf-8")
    csv.write('filePath\tcustomer_id\tcustomer_name\tfeed_id\tfeed_name\tfeed_property\tfeed_key\tfeed_format\tfeed_link\n')
    for filePath in json_paths:
        with open(filePath) as json_file:
            data = json.load(json_file)
            idCustomer=''
            nameCustomer=''
            for item in data: 
                if 'nameCustomer' in item:
                    idCustomer = getProp('idCustomer', item)
                    nameCustomer = getProp('nameCustomer', item)
                elif 'feedID' in item:
                    if 'publications' in item:
                        publications = item['publications']
                        if 'http' in publications:
                            http = publications['http']
                            for (http_prop, http_val) in http.items():
                                csv.write(filePath + '\t' + idCustomer + '\t' + nameCustomer + '\t' + item['feedID'] + '\t' +  item['feedName'] + '\t' + http_prop + '\t' + http_val['key'] + '\t' + http_val['format'] + '\t' + http_val['ecodeLink'] + '\n')
                        else:
                            csv.write(filePath + '\t' + idCustomer + '\t' + nameCustomer + '\t' + item['feedID'] + '\t' +  item['feedName'] + '\t\t\t\t\n')
                    else:
                        csv.write(filePath + '\t' + idCustomer + '\t' + nameCustomer + '\t' + item['feedID'] + '\t' +  item['feedName'] + '\t\t\t\t\n')
    csv.close()

try:
    action = sys.argv[1]
    if action == 'newsletters':
        if len(sys.argv) >2:
            rootFolder = sys.argv[2]
            debug = False
            dump_newsletters(rootFolder)
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
    print(ex)
    print("usage: python monitor.py feeds <path_to_folder>")
    print("       python monitor.py newsletters <path_to_folder>")




