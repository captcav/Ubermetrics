# coding=utf-8
import os
import csv

path = '.\\files\\'
files = []

for r, d, f in os.walk(path):
    for file in f:
        if '.csv' in file:
            files.append(os.path.join(r, file))

merged_file = open('merge.csv', 'w+', encoding="utf-8")
merged_file.write('search_id\tsearch_name\tfolder_id\tfolder_name\taccount_login\taccount_password\n')
for f in files:
    with open(f, encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        for row in csv_reader:
            merged_file.write(row[0] + '\t' + row[1] + '\t' + row[2] + '\t' + row[3] + '\t' + row[4] + '\t' + row[5] + '\n')
    
