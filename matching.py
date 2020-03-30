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
            #filePath	customer_id	customer_name	feed_id	feed_name	feed_property	feed_key	feed_format	feed_link
            file_path=row[0]
            customer_id=row[1]
            customer_name=row[2]
            feed_id=row[3]
            feed_name=row[4]
            feed_property=row[5]
            feed_key=row[6]
            feed_format=row[7]
            feed_link=row[8]
            t = search_config(customer_name, feed_name, tree)
            if t is not None:
                line = feed_id + '\t' + file_path + '\t' + customer_id + '\t' + customer_name + '\t' + feed_name + '\t' + t.login + '\t' + t.password + '\t' + t.name + '\t' + t.label + '\t' + t.type
                print(line)
                f.write(line + '\n')
            else:
                f.write(feed_id + '\t' + file_path + '\t' + customer_id + '\t' + customer_name + '\t' + feed_name + '\t\t\t\t\t\n')

def match_all(tree):
    f = open('matching.csv', 'w+', encoding="utf-8")
    f.write('json_feedId' + '\t' + 'json_filepath' + '\t' + 'json_customer_id' + '\t' + 'json_customer_name' + '\t' + 'json_feedName' + '\t' + 'ub_login' + '\t' + 'ub_password' + '\t' + 'ub_name' + '\t' + 'ub_label' + '\t' + 'ub_type' + '\n')
    match_feeds(tree, f)
    f.close()

f = open(r'ubermetrics.pkl', 'rb')
tree = pickle.load(f)
f.close()

match_all(tree)
