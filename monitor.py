# coding=utf-8
import sys 
import os
import json
import api

def dump_newsletter(filePath, idCustomer, nameCustomer, newsletters, csv): 
    for (k, v) in newsletters.items():
        line = k 
        line += '\t' + api.get_prop('design_format', v)
        line += '\t' + api.get_prop('design_title', v)
        line += '\t' + api.get_prop('logoUrl', v)
        line += '\t' + api.get_prop('primaryColor', v)
        line += '\t' + api.get_prop('hour', v)
        line += '\t' + api.get_prop('min', v)
        line += '\t' + api.get_prop('hour2', v)
        line += '\t' + api.get_prop('min2', v)
        line += '\t' + api.get_prop('valuation_to_show', v)
        line += '\t' + api.get_prop('order_by', v)
        line += '\t' + api.get_prop('grouping', v)
        line += '\t' + api.get_prop('num_mentions', v)
        line += '\t' + api.get_prop('email', v)
        line += '\t' + api.get_prop('selection', v)
        line += '\t' + api.get_prop('name_remitent', v)
        line += '\t' + api.get_prop('charset', v)
        line += '\t' + api.get_prop('type', v)
        line += '\t' + api.join_prop('days', v, '|')
        if 'list' in v:
            line += '\t' + str(len(v['list']))
        else:
            line += '\t'
        line += '\t' + api.join_prop('list', v, ';')

        if 'feeds' not in v:
            csv.write(filePath + '\t' + idCustomer + '\t' + nameCustomer + '\t' + line + '\t\t\t\t\t\t\t\n')
        else:
            feeds = v['feeds']
            for (ke, va) in feeds.items():
                feedLine = ke   
                feedLine += '\t' + api.get_prop('valuation_to_show', va)
                feedLine += '\t' + api.get_prop('order_by', va)
                feedLine += '\t' + api.get_prop('selection', va)
                feedLine += '\t' + api.get_prop('grouping', va)                
                feedLine += '\t' + api.get_prop('feedName', va)                
                feedLine += '\t' + api.get_prop('num_mentions', va)
                csv.write(filePath + '\t' + idCustomer + '\t' + nameCustomer + '\t' + line + '\t' + feedLine + '\n')

def dump_newsletters(json_paths):
    print('extracting newsletters from JSON files csv...')
    default_headers = 'file_path \t idCustomer \t name_customer \t newsletter_id \t newsletter_design_format \t newsletter_design_title \t logo_url \t primary_color \t newsletter_hour \t newsletter_min \t newsletter_hour2 \t newsletter_min2 \t newsletter_valuation_to_show \t newsletter_order_by \t newsletter_grouping \t newsletter_num_mentions \t newsletter_email \t newsletter_selection \t newsletter_name_remitent \t newsletter_charset \t newsletter_type \t newsletter_days \t newsletter_nb_list \t newsletter_list'
    csv = open('json_newsletters.csv', 'w+', encoding="utf-8")
    csv.write(default_headers + '\t feed_id \t feed_valuation_to_show \t feed_order_by \t feed_ selection \t feed_grouping \t feed_feedName \t feed_num_mentions \n')
  
    for filePath in json_paths:
        with open(filePath) as json_file:
            try:
                data = json.load(json_file)
                print(filePath + ': OK')
            except Exception as ex:
                print(filePath + ': ' + str(ex))
                continue
            
            for item in data:
                if 'module' in item:
                    module =item['module']
                    if 'newsletter' in module:
                        newsletters = module['newsletter']
                        nameCustomer = api.get_prop('nameCustomer', item)
                        idCustomer = api.get_prop('idCustomer', item)
                        dump_newsletter(filePath,idCustomer, nameCustomer, newsletters, csv)
    csv.close()

def dump_feeds(json_paths):
    print('extracting feeds from JSON files csv...')
    csv = open('json_feeds.csv', 'w+', encoding="utf-8")
    csv.write('filePath\tcustomer_id\tcustomer_name\tfeed_id\tfeed_name\tfeed_property\tfeed_key\tfeed_format\tfeed_link\n')
    for filePath in json_paths:
        with open(filePath) as json_file:
            try:
                data = json.load(json_file)
                print(filePath + ': OK')
            except Exception as ex:
                print(filePath + ': ' + str(ex))
                continue
            
            idCustomer=''
            nameCustomer=''
            for item in data: 
                if 'nameCustomer' in item:
                    idCustomer = api.get_prop('idCustomer', item)
                    nameCustomer = api.get_prop('nameCustomer', item)
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
    if len(sys.argv) < 3:
        raise Exception('missing argument')
    
    json_paths = api.get_JSON_filepaths(sys.argv[2])

    if sys.argv[1] == '-news':
        dump_newsletters(json_paths)
    elif sys.argv[1] == '-feeds':
        dump_feeds(json_paths)
    elif sys.argv[1] == '-both':
        dump_feeds(json_paths)
        dump_newsletters(json_paths)
    else:
        raise Exception("action undefined: " + sys.argv[1]) 
except Exception as ex:
    print(ex)
    print("usage: python monitor.py feeds <path_to_folder>")
    print("       python monitor.py newsletters <path_to_folder>")
    print("       python monitor.py both <path_to_folder>")
