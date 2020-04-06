import os
import json
import api
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

def build_tree(node, items, login, password):
    if 'children' in node : 
        children = []
        for child in node['children']:
            id = child["_reference"]
            childNode = [x for x in items if x['name']==id][0]
            children.append(build_tree(childNode, items, login, password))
        return Tree(node, children, login, password)
    else:
        return Tree(node, None, login, password)

def dump_ubermetrics_searches(login, password):
    data = {}
    data = api.connect(login, password)
    tree = api.get_search_tree({
        'user_id': data["user_id"], 
        'session_id': data["session_id"], 
        'auth_token': data["auth_tokens"].pop(),
    })
    
    items = tree['items']
    root = [x for x in items if x['name']=='#all'][0]
    
    return build_tree(root, items, login, password)

def print_node(node, str = ''):
    if str == '':
        str = '(' + node.login + ', ' + node.password + ')'
    else:
        str = str + ' -> ' + '(' + node.name + ', ' + node.type + ', ' + node.label + ')'
    print(str)
    if node.children is not None:
        for child in node.children:
            print_node(child, str)


def getProp(property, obj):
    if property in obj:
        value = obj[property]
        if value is None: 
            return ''
        else:
            return value
    else:
        return ''

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

class Feed(object):
    def __init__(self, file_path, customer_id, customer_name, feed_id, feed_name, feed_property='', feed_key='', feed_format='', feed_link=''):
        self.file_path = file_path
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.feed_id = feed_id
        self.feed_name = feed_name
        self.feed_property = feed_property
        self.feed_key = feed_key
        self.feed_format = feed_format
        self.feed_link = feed_link
        self.ub_login = ''
        self.ub_password = ''	
        self.ub_name = ''	
        self.ub_label = ''	
        self.ub_type = ''
    
    def __repr__(self):
        return self.file_path + '\t' + self.customer_id + '\t' + self.customer_name + '\t' + self.feed_id + '\t' +  self.feed_name + '\t' + self.feed_property + '\t' + self.feed_key + '\t' + self.feed_format + '\t' + self.feed_link + '\t' + self.ub_login + '\t' + self.ub_password + '\t' + self.ub_name + '\t' + self.ub_label + '\t' + self.ub_type

def extract_monitor_feeds(folder_path):
    feeds = []
    json_paths = getJsonFilePaths(folder_path)
    for filePath in json_paths:
        with open(filePath) as json_file:
            data = None
            try:
                data = json.load(json_file)
            except Exception as ex:
                print('----> error : ' + filePath + ' -> ' + str(ex))
                continue
            
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
                                feeds.append(Feed(
                                    file_path=filePath,
                                    customer_id= idCustomer,
                                    customer_name= nameCustomer,
                                    feed_id=item['feedID'],
                                    feed_name=item['feedName'],
                                    feed_property=http_prop,
                                    feed_key=http_val['key'],
                                    feed_format=http_val['format'],
                                    feed_link=http_val['ecodeLink']        
                                ))
                        else:
                            feeds.append(Feed(
                                file_path=filePath,
                                customer_id= idCustomer,
                                customer_name= nameCustomer,
                                feed_id=item['feedID'],
                                feed_name=item['feedName']
                            ))
                    else:
                        feeds.append(Feed(
                            file_path=filePath,
                            customer_id= idCustomer,
                            customer_name= nameCustomer,
                            feed_id=item['feedID'],
                            feed_name=item['feedName']
                        ))
    return feeds

def match_feeds(feeds, searches, f):
    if searches is None:
        return 

    for feed in feeds:
        match = search_config(feed.customer_name, feed.feed_name, searches)
        if match is not None:
            feed.ub_login = match.login
            feed.ub_password = match.password
            feed.ub_name = match.name
            feed.ub_label = match.label
            feed.ub_type = match.type

def do_matching(monitor_file_path, ub_credentials):
    print('# Monitor to Ubermetrics : "' + monitor_file_path)
    print('----> extracting Monitor feeds from "' + monitor_file_path + '"...')
    feeds = extract_monitor_feeds(monitor_file_path)

    searches = None
    if type(ub_credentials) == tuple:
        ub_login = ub_credentials[0]
        ub_password = ub_credentials[1]
        print('----> requesting Ubermetrics searches for (' + ub_login + ', ' + ub_password + ')...')
        try:
            searches = dump_ubermetrics_searches(ub_login, ub_password)
        except Exception as ex:
            print('----> error : ' + str(ex))
    elif type(ub_credentials) == list:
        searches = Tree({"name":"root", "label":"root","type":"root"}, children=None)
        for credentials in ub_credentials:
            ub_login = credentials[0]
            ub_password = credentials[1]
            print('----> requesting Ubermetrics searches for (' + ub_login + ', ' + ub_password + ')...')
            try:
                search = dump_ubermetrics_searches(ub_login, ub_password)
                if search is not None:
                    searches.add_child(search)
            except Exception as ex:
                print('----> error : ' + str(ex))
    else:
        print('----> error : unsupported argument for credentials : ' + str(type(ub_credentials)))

    #print_node(searches)
    print('----> matching Monitor with Ubermetrics searches...')
    match_feeds(feeds, searches, None) 

    return feeds

def print_matchings(monitor_file_path, ub_credentials):
    feeds = do_matching(monitor_file_path, ub_credentials)
    for feed in feeds:
        print(str(feed))

def get_folder_name(path): 
    parts = path.split('/')
    return parts[len(parts)-1]

def write_matchings_internal(monitor_file_path, ub_credentials, f):
    monitor_folder_name = get_folder_name(monitor_file_path)
    feeds = do_matching(monitor_file_path, ub_credentials)
    for feed in feeds:
        f.write(monitor_folder_name + '\t' + str(feed) + '\n')

def write_matchings(configs):
    results_file_name = 'matchings/matchings.all.csv'
    if len(configs) == 1:
        monitor_folder_name = get_folder_name(configs[0][0])
        results_file_name = 'matchings/matchings.' + monitor_folder_name + '.csv'
    
    f = open(results_file_name, 'w+', encoding="utf-8")
    f.write('folder_name' + '\t' + 'json_file_path' + '\t' + 'json_customer_id' + '\t' + 'json_customer_name' + '\t' + 'json_feed_id' + '\t' +  'json_feed_name' + '\t' + 'json_feed_property' + '\t' + 'json_feed_key' + '\t' + 'json_feed_format' + '\t' + 'json_feed_link' + '\t' + 'ub_login' + '\t' + 'ub_password' + '\t' + 'ub_name' + '\t' + 'ub_label' + '\t' + 'ub_type' + '\n')
    for config in configs:
        monitor_file_path = config[0]
        ub_credentials = config[1]
        write_matchings_internal(monitor_file_path, ub_credentials, f)
        print('----> saving results in ' + results_file_name + '...')
    f.close()

configs = [
	("./json/fixv6.0/admirabilia",("Admirabilia-Augure","augure20")),
	("./json/fixv6.0/almirall", ("","augure20")),
	("./json/fixv6.0/amalthea", ("Amalthea-Augure","augure20")),
	("./json/fixv6.0/anniebonnie", ("Anniebonnie-Augure","augure20")),
	("./json/fixv6.0/artelier", ("Artelier-Augure","augure20")),
	("./json/fixv6.0/berbes", ("Berbes-Augure","augure20")),
	("./json/fixv6.0/bluwom", ("Bluwom-Augure","augure20")),
	("./json/fixv6.0/bradek", ("Bradek-Augure","augure20")),
	("./json/fixv6.0/bursonmarstelleremea", ("BursonEmea-Augure","augure20")),
	("./json/fixv6.0/comunicacionibero", ("Comunicacionibero-Augure","augure20")),
	("./json/fixv6.0/crc", ("CRC-Augure","augure20")),
	("./json/fixv6.0/deva", ("Deva-Augure","augure20")),
	("./json/fixv6.0/europapress", ("","augure20")),
	("./json/fixv6.0/evercom", ("Evercom-Augure","augure20")),
	("./json/fixv6.0/finalCustomers", [("France-Augure", "augure20"), ("Spain-Augure","augure20")]),
	("./json/fixv6.0/gaiacomunicacion", ("Gaiacomunicacion-Augure","augure20")),
	("./json/fixv6.0/havaspr", ("Havas-Augure","augure20")),
	("./json/fixv6.0/keima", ("Keima-Augure","augure20")),
	("./json/fixv6.0/lewis", ("Lewis-Augure","augure20")),
	("./json/fixv6.0/littlewing", ("Littlewing-Augure","augure20")),
	("./json/fixv6.0/marco", ("Marco-Augure","augure20")),
	("./json/fixv6.0/onecomunicacion", ("Onecomunicacion-Augure","augure20")),
	("./json/fixv6.0/prisma", ("Prisma-Augure","augure20")),
	("./json/fixv6.0/theoria", ("Theoria-Augure","augure20")),
	("./json/fixv6.0/torresycarrera", ("Torresycarrera-Augure","augure20"))
]

#print(type(configs[0][0]))
#print(str(type(configs[0][1])))
write_matchings(configs)

