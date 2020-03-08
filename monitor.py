# coding=utf-8
import sys 
import os
import csv
import json

def dump_config(json_path, csv):
    with open(json_path) as json_file:
        data = json.load(json_file)
        nameCustomer = ''
        for item in data: 
            if 'nameCustomer' in item: 
                nameCustomer = item['nameCustomer'] 
            elif 'feedID' in item:
                line = item['feedID'] + '\t' + json_path + '\t' + nameCustomer + '\t' +  item['feedName']
                csv.write(line + '\n')
                print(line)

def dump_all():
    filepath = 'configurations'
    files_and_folders = [f for f in os.scandir(filepath)]
    csv = open('monitor.csv', 'w+', encoding="utf-8")
    csv.write( 'feedId' + '\t' + 'filePath' + '\t' 'customerName' + '\t' + 'feedName'  + '\n')
    for f in files_and_folders:
        if f.is_dir():
            d = os.path.join(filepath, f.name)
            filenames = os.listdir(d)
            for filename in filenames:
                json_path = os.path.join(d, filename) 
                dump_config(json_path, csv)
        else:
            json_path = os.path.join(filepath, f.name)
            dump_config(json_path, csv)
    csv.close()

dump_all()

