# coding=utf-8
import sys 
import os
import json
import api
import commons

def dump_newsletter(filePath, idCustomer, nameCustomer, newsletters, csv): 
    for (k, v) in newsletters.items():
        line = k 
        line += '\t' + commons.get_prop('newsletter_name', v)
        line += '\t' + commons.get_prop('subject', v)
        line += '\t' + commons.get_prop('design_format', v)
        line += '\t' + commons.get_prop('design_title', v)
        line += '\t' + commons.get_prop('logoUrl', v)
        line += '\t' + commons.get_prop('primaryColor', v)
        line += '\t' + commons.get_prop('hour', v)
        line += '\t' + commons.get_prop('min', v)
        line += '\t' + commons.get_prop('hour2', v)
        line += '\t' + commons.get_prop('min2', v)
        line += '\t' + commons.get_prop('valuation_to_show', v)
        line += '\t' + commons.join_prop('orderShowSearch', v, '|')
        line += '\t' + commons.get_prop('grouping', v)
        line += '\t' + commons.get_prop('num_mentions', v)
        line += '\t' + commons.get_prop('email_to', v)
        line += '\t' + commons.get_prop('email_remitent', v)
        line += '\t' + commons.get_prop('selection', v)
        line += '\t' + commons.get_prop('name_remitent', v)
        line += '\t' + commons.get_prop('charset', v)
        line += '\t' + commons.get_prop('type', v)
        line += '\t' + commons.join_prop('days', v, '|')
        if 'list' in v:
            line += '\t' + str(len(v['email_list_to']))
        else:
            line += '\t'
        line += '\t' + commons.join_prop('email_list_to', v, ';')

        if 'feeds' not in v:
            csv.write(filePath + '\t' + idCustomer + '\t' + nameCustomer + '\t' + commons.normalized(nameCustomer) + '\t' + line + '\t\t\t\t\t\t\t\t\n')
        else:
            feeds = v['feeds']
            for (ke, va) in feeds.items():
                feedLine = ke   
                feedLine += '\t' + commons.get_prop('valuation_to_show', va)
                feedLine += '\t' + commons.get_prop('order_by', va)
                feedLine += '\t' + commons.get_prop('selection', va)
                feedLine += '\t' + commons.get_prop('grouping', va)
                feedName = commons.get_prop('feedName', va)         
                feedLine += '\t' + feedName + '\t' + commons.normalized(feedName)
                feedLine += '\t' + commons.get_prop('num_mentions', va)
                csv.write(filePath + '\t' + idCustomer + '\t' + nameCustomer + '\t' + commons.normalized(nameCustomer) + '\t' + line + '\t' + feedLine + '\n')

def dump_newsletters(json_paths):
    print('extracting newsletters from JSON files csv...')
    default_headers = 'file_path\tidCustomer\tname_customer\tnormalized_customer_name\tnewsletter_id\tnewsletter_name\tnewsletter_subject\tnewsletter_design_format\tnewsletter_design_title\tlogo_url\tprimary_color\tnewsletter_hour\tnewsletter_min\tnewsletter_hour2\tnewsletter_min2\tnewsletter_valuation_to_show\tnewsletter_order_by\tnewsletter_grouping\tnewsletter_num_mentions\tnewsletter_email_to\tnewsletter_email_remitent\tnewsletter_selection\tnewsletter_name_remitent\tnewsletter_charset\tnewsletter_type\tnewsletter_days\tnewsletter_nb_list_to\tnewsletter_list_to'
    csv = open('./output/json_newsletters.csv', 'w+', encoding="utf-8")
    csv.write(default_headers + '\tfeed_id\tfeed_valuation_to_show\tfeed_order_by\tfeed_selection\tfeed_grouping\tfeed_feedName\tnormalized_feedName\tfeed_num_mentions\n')
  
    for filePath in json_paths:
        with open(filePath) as json_file:
            try:
                data = json.load(json_file)
                print(filePath + ': OK')
            except Exception as ex:
                print(filePath + ': ' + str(ex))
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
                        dump_newsletter(filePath,idCustomer, nameCustomer, newsletters, csv)
    csv.close()

def dump_feeds(json_paths):
    print('extracting feeds from JSON files csv...')
    csv = open('./output/json_feeds.csv', 'w+', encoding="utf-8")
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
                if item is None:
                    continue
                
                if 'nameCustomer' in item:
                    idCustomer = commons.get_prop('idCustomer', item)
                    nameCustomer = commons.get_prop('nameCustomer', item)
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
    
    json_paths = commons.get_json_filepath(sys.argv[2])

    if sys.argv[1] == '-newsletters':
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
    print("usage: python monitor.py -feeds <path_to_folder>")
    print("       python monitor.py -newsletters <path_to_folder>")
    print("       python monitor.py -both <path_to_folder>")
