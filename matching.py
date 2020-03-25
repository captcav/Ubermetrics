import pickle
import csv
from tree import Tree

def search_by(str, tree, search_type):
    if (search_type=='label' and tree.label.lower()==str.lower()) or (search_type=='name' and tree.name.lower()==str.lower()):
        return tree
    elif tree.type=='search':
        return None
    else:
        for child in tree.children:
            found=search_by(str, child, search_type)
            if found is not None:
                return found
    return None

def search_by_name(str, tree):
    return search_by(str,tree, 'name')

def search_by_label(str, tree):
    return search_by(str,tree, 'label')

def search_config(customerName, feedName, tree):
    customer = search_by_label(customerName, tree)
    if customer is not None:
        for child in customer.children:
            feed = search_by_label(feedName, child) 
            if feed is not None:
                return feed
    return None

def match_feeds(tree, f):
    with open('json_feeds.csv', encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        next(csv_reader) #escape header
        for row in csv_reader:
            file = row[0]
            customer = row[1]
            feedId = row[2]
            feedName = row[3]
            t = search_config(customer, feedName, tree)
            if t is not None:
                line = feedId + '\t' + file + '\t' + customer + '\t' + feedName + '\t' + t.login + '\t' + t.password + '\t' + t.name + '\t' + t.label + '\t' + t.type
                print(line)
                f.write(line + '\n')
            else:
                f.write(feedId + '\t' + file + '\t' + customer + '\t' + feedName + '\t\t\t\t\t\n')

def match_all(tree):
    f = open('matching.csv', 'w+', encoding="utf-8")
    f.write('json_feedId' + '\t' + 'json_filepath' + '\t' + 'json_customer' + '\t' + 'json_feedName' + '\t' + 'ub_login' + '\t' + 'ub_password' + '\t' + 'ub_name' + '\t' + 'ub_label' + '\t' + 'ub_type' + '\n')
    match_feeds(tree, f)
    f.close()

f = open(r'ubermetrics.pkl', 'rb')
tree = pickle.load(f)
f.close()

match_all(tree)
