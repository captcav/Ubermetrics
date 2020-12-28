# coding=utf-8
import json
import urllib.parse
import urllib.request
import hashlib
import os
import unidecode
import commons
from api_google_sheet import get_ubermetrics_accounts
import api_salesforce
import pyodbc 

from dotenv import load_dotenv
load_dotenv()

def request_api(params):
    url = os.getenv("UB_API_ENDPOINT")
    encoded_params = urllib.parse.urlencode(params)
    encoded_params = encoded_params.encode('ascii') # data should be bytes
    req = urllib.request.Request(url, encoded_params)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())

def connect(login, password): 
    login_request = request_api({'action' : 'login_request','user_name' : login})
    if login_request['success'] != 'true':
        raise Exception(login_request['error']['message'])
        
    user_data = login_request['data']
    user_id = user_data['user_id']
    user_seed = user_data['user_seed']
    auth_seed = user_data['auth_seed']
    md5Pass = hashlib.md5(password.encode())
    md5WithUser = hashlib.md5((md5Pass.hexdigest() + user_seed).encode())
    md5WithAuth = hashlib.md5((md5WithUser.hexdigest() + auth_seed).encode())

    login = request_api({'action' : 'login', 'user_id' : user_id, 'pass' : md5WithAuth.hexdigest()})
    if login['success'] != 'true':
        raise Exception(login['error']['message'])
    
    data = login["data"]
    return {
        "user_id": user_id,
        "session_id": data['session_id'],
        "auth_tokens": data['auth_tokens']
    }

def get_search_tree(options):
    response = request_api({
        'action':'get_search_tree', 
        'user_id': options["user_id"], 
        'session_id': options["session_id"], 
        'auth_token': options["auth_token"],
        'marked':-1, 
        'sentiment': -1, 
        'read': -1, 
        'critical': -1, 
        't_max': '2012-12-01 00:00:00', 
        't_min': '2012-12-01 00:00:00',
        'language': '', 
        'group_type': ''
    })
    if response['success'] != 'true':
        raise Exception(response['error']['message'])
    
    tree = response["data"]
    return {
        "prop_label":tree['label'],
        "prop_identifier": tree['identifier'],
        "items": tree['items']
    }

def get_ub_active_accounts(isAPI:bool):
    print('retrieve accounts list from Ubermetrics Google Sheet...')
    ub_accounts = get_ubermetrics_accounts()

    accounts = []
    for row in ub_accounts:
        if len(row) == 3 and (row[2]=='in use' or row[2] == 'Account created'):
            accounts.append([row[1] if isAPI else row[0], os.getenv("UB_DEFAULT_PASSWORD"), row[2]])  
    accounts.append(['demoagency', 'demo2020', 'in use'])
    accounts.append(['demofinal', 'demo2020', 'in use'])

    return accounts 

def get_sf_applications():
    print('retrieve Publisher applications from Salesforce...')
    return api_salesforce.get_sf_apps()

def process_all_accounts(working_folder, isAPI): 
    ub_accounts = list(get_ub_active_accounts(isAPI))
    sf_apps = get_sf_applications()
    
    results = []
    for folder in os.scandir(working_folder):
        if not folder.is_dir:
            continue
        info = process_account(folder.name, folder.path, ub_accounts, sf_apps)
        results.append(info)
    return results

def process_one_account(folder_path:str, isAPI:bool = True):
    ub_accounts = list(get_ub_active_accounts(isAPI))
    sf_apps = get_sf_applications()

    results = []
    folder_name = commons.get_folder_name(folder_path)
    info = process_account(folder_name, folder_path, ub_accounts, sf_apps)
    results.append(info)
    return results

def process_account(folder_name:str, folder_path:str, ub_accounts:list, sf_apps:list):
        # guess Publisher application URL 
        application_url = []
        if folder_name == 'marco':
            application_url.append("https://marcodecomunicacion.hosting.augure.com/Augure_MdCom")
        elif folder_name == 'demo_agency':
            application_url.append('https://demo.hosting.augure.com/Demo_Agencia')
        elif folder_name == 'certina' or folder_name == 'rado' or folder_name == 'swatch':
            application_url.append('https://mra.hosting.augure.com/Augure_MRA')   
        elif folder_name == 'mayoral':
            application_url.append('https://ra.hosting.augure.com/Augure_RA')   
        elif folder_name == 'elanedelman':
            application_url.append('https://agenceee.hosting.augure.com/Augure_EE')
        elif folder_name == 'oxfaminternational':
            application_url.append('https://intermonoxfam.hosting.augure.com/Augure_IntermonOxfam')            
        elif folder_name == 'mapfre':
             application_url.append("https://mapfre.hosting.augure.com/Augure_Mapfre")
        elif folder_name == 'repsolsa':
            application_url.append("https://repsol.hosting.augure.com/Augure_Repsol")
        elif folder_name != 'france' and folder_name != 'spain':
            f1_name = folder_name
            f1_name = unidecode.unidecode(folder_name)

            dict = {
                "bursonmarstelleremea":"bmie",
                "elanedelman":"Elan Edelman",
                "spencerlewis":"Spencer & Lewis",
                "muséenature":"Musée de la Chasse et de la Nature",
                "interfacespain":"Interface Tourism Group",
                "gaiacomunicacion":"gaia",
                "frederiqueconstant":"Frederique Constant",
                "eolocomunicación":"eolo",
                "nintendo":"Nintendo SP",
                "lewis":"Lewis Communications SL"
            }

            if folder_name in dict:
                f1_name = dict[folder_name]

            arr =[]
            for app in sf_apps:
                if f1_name in app['name'] or f1_name in app['url'] or f1_name in app['account']['name']:  
                    arr.append(app['url'])
                elif app['name'].lower().find(f1_name,0) >= 0 or app['url'].lower().find(f1_name,0) >= 0 or app['account']['name'].lower().find(f1_name,0) >= 0:
                    arr.append(app['url'])

            application_url = arr
        
        # normalized JSON folder name 
        folder_normalized = folder_name
        if folder_name == 'eliotrope':
            folder_normalized = 'eliotrop'
        elif folder_name == 'demo_rp':
            folder_normalized = 'demofinal'
        elif folder_name == 'demo_agency':
            folder_normalized = 'demoagency'
        elif folder_name == 'interfacespain':
            folder_normalized = 'interface'
        elif folder_name == 'oxfaminternational':
            folder_normalized = 'oxfamiternational'

        # get Ubermetrics info 
        ub_info = None
        for ub_account in ub_accounts:
            if ub_account[0].replace('-Augure','').replace('-API', '').lower() == folder_normalized.lower():
                ub_info = (ub_account[0], ub_account[1])
                break
        
        return (folder_path, ub_info, folder_normalized, application_url)

def save_ub_accounts(accounts):
    serverName='.'
    databaseName='UbermetricsMigration'
    conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                'Server=' + serverName + ';'
                'Database=' + databaseName + ';'
                'Trusted_Connection=yes;')
    
    cursor = conn.cursor()
    stmt = """DELETE FROM dbo.[ub.accounts]"""
    cursor.execute(stmt)
    
    stmt = """INSERT INTO dbo.[ub.accounts] (provider_name, login, password, app_url, folder_path) VALUES (?, ?, ?, ?, ?)"""
    cursor.executemany(stmt, accounts)
    conn.commit()
    conn.close()
    print('deleting exiting entries and inserting {} new entries into dbo.[ub.accounts]'.format(len(accounts)))
   
def save_augure_apps(apps):
    serverName='.'
    databaseName='UbermetricsMigration'
    conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                'Server=' + serverName + ';'
                'Database=' + databaseName + ';'
                'Trusted_Connection=yes;')
    
    cursor = conn.cursor()
    stmt = """DELETE FROM dbo.[augure.apps]"""
    cursor.execute(stmt)
    
    stmt = """INSERT INTO dbo.[augure.apps] (id, name, url, frontServer, backServer, language, account_name,account_tier) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
    cursor.executemany(stmt, apps)
    conn.commit()
    conn.close()
    print('deleting existing entries and inserting {} new entries into dbo.[augure.apps]'.format(len(apps)))

def save_uberfactory_feeds():
    stmt = (" SELECT DISTINCT monitor_feed_id"
            " FROM [CUSTOMERS] c"
	        "   INNER JOIN SCHEDULE s ON s.Customer_ID = c.Customer_ID"
	        "   INNER JOIN ub_new_customers u ON u.new_customer_id = c.Customer_ID"
            " WHERE s.Schedule_Status=1")

    serverName='ah0801.hosting.augure.com'
    databaseName='UberFactory'
    userId = os.getenv("SQL_USERID")
    password = os.getenv("SQL_PASSWORD")
    conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                'Server=' + serverName + ';'
                'Database=' + databaseName + ';'
                'UID=' + userId + ';'
                'PWD=' + password + ';')

    cursor = conn.cursor()
    cursor.execute(stmt)
    activeFeeds = cursor.fetchall()
    print("retrieving {} active feeds from the UberFactory".format(len(activeFeeds)))

    serverName='.'
    databaseName='UbermetricsMigration'
    conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                'Server=' + serverName + ';'
                'Database=' + databaseName + ';'
                'Trusted_Connection=yes;')
    
    cursor = conn.cursor()
    stmt = """DELETE FROM dbo.[uberfactory]"""
    cursor.execute(stmt)
    print('deleting existing entries in dbo.[uberfactory]')

    stmt = """INSERT INTO dbo.[uberfactory] (feed_id) VALUES (?)"""
    cursor.executemany(stmt, activeFeeds)
    conn.commit()
    conn.close()
    print('inserting {} new entries into dbo.[uberfactory]'.format(len(activeFeeds)))

    return activeFeeds

def get_factory_feeds():
    stmt = ("SELECT T.*"
            ", LEFT(SUBSTRING(T.Source_Path, CHARINDEX('clau=', T.Source_Path)+5, 100), CHARINDEX('&', SUBSTRING(T.Source_Path, CHARINDEX('clau=', T.Source_Path)+5, 100))-1) as Monitor_Key"
            " FROM ("
	        " SELECT CF.Customer_ID"
	        ", C.Customer_Name"
        	", C.Destination_Path"
        	", P.ProviderFTP"
        	", REPLACE(REPLACE(CF.Source_Path,'ecode.cgi?', 'ccode.cgi?clau='),'ccode.cgi?lvRd2VAkWbwbtXG8QwKK','ccode.cgi?clau=lvRd2VAkWbwbtXG8QwKK') + '&' as Source_Path"
        	", C.ApplicationUrl"
        	", CASE "
        	"   WHEN ApplicationURL IS NULL OR LEN(ApplicationUrl)=0 THEN SUBSTRING(Customer_Name,1, CHARINDEX('_', Customer_Name, 8) - 1)"
        	"   ELSE SUBSTRING(ApplicationUrl, CHARINDEX('/', ApplicationUrl,10) +1, 100)"
        	" END as 'ApplicationName'"
        	" FROM [Factory].[dbo].[CUSTOMER_FILE_DETAILS] CF"
        	"       INNER JOIN SCHEDULE S ON S.Customer_ID=CF.Customer_ID"
        	"       INNER JOIN CUSTOMERS C ON C.Customer_ID=CF.Customer_ID"
        	"       INNER JOIN [PROVIDER] P ON P.Provider_ID = C.Provider_Id"
        	"   WHERE C.Provider_Id in (261, 481)  AND S.Schedule_Status=1"
        	"   AND C.Customer_Name not like ('Imente_DKV_%')"
        	"   AND C.Customer_Name not like ('Augure_Pandora_%')"
        	"   AND C.Customer_Name not like ('Augure_GStarRAW_%')"
        	"   AND C.Customer_Name not like ('Augure_SC_SerenaCapital%')"
        	"   AND (CF.Source_Path not like '%7hLwqORNEUWoJ.b7gNpjz1%') " #exclude Imente_DemoAuto_SM
        	"   AND (CF.Source_Path not like '%lvRd2VAkWbwbtXG8QwKK%') " # exclude Imente_DemoListen_VehiculesElectriques_ok
            ") AS T "
            "ORDER BY T.Customer_Name")
    
    serverName='ah0801.hosting.augure.com'
    databaseName='Factory'
    userId = os.getenv("SQL_USERID")
    password = os.getenv("SQL_PASSWORD")
    conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                'Server=' + serverName + ';'
                'Database=' + databaseName + ';'
                'UID=' + userId + ';'
                'PWD=' + password + ';')

    cursor = conn.cursor()
    cursor.execute(stmt)
    result = cursor.fetchall()

    print("retrieving {} feeds from the Factory".format(len(result)))
    return result

def save_factory_feeds(feeds):
    serverName='.'
    databaseName='UbermetricsMigration'
    conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                'Server=' + serverName + ';'
                'Database=' + databaseName + ';'
                'Trusted_Connection=yes;')
    
    cursor = conn.cursor()
    stmt = """DELETE FROM dbo.[factory_feeds]"""
    cursor.execute(stmt)
    
    stmt = """INSERT INTO dbo.[factory_feeds] (Customer_ID, Customer_Name, Destination_Path, ProviderFTP, Source_Path, ApplicationUrl, ApplicationName, Monitor_Key) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
    cursor.executemany(stmt, feeds)
    conn.commit()
    conn.close()
    print('deleting existing entries and inserting {} new entries into dbo.[factory_feeds]'.format(len(feeds)))

def save_monitor_newsletters(newsletters):
    serverName='.'
    databaseName='UbermetricsMigration'
    conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                'Server=' + serverName + ';'
                'Database=' + databaseName + ';'
                'Trusted_Connection=yes;')
    
    cursor = conn.cursor()
    stmt = """DELETE FROM [dbo].[json_newsletters]"""
    cursor.execute(stmt)
    
    stmt = ("INSERT INTO [dbo].[json_newsletters]"
           "([file_path]"
           ",[idCustomer]"
           ",[name_customer]"
           ",[normalized_customer_name]"
           ",[newsletter_id]"
           ",[newsletter_name]"
           ",[newsletter_subject]"
           ",[newsletter_design_format]"
           ",[newsletter_design_title]"
           ",[logo_url]"
           ",[primary_color]"
           ",[newsletter_hour]"
           ",[newsletter_min]"
           ",[newsletter_hour2]"
           ",[newsletter_min2]"
           ",[newsletter_valuation_to_show]"
           ",[newsletter_order_by]"
           ",[newsletter_grouping]"
           ",[newsletter_num_mentions]"
           ",[newsletter_email_to]"
           ",[newsletter_email_remitent]"
           ",[newsletter_selection]"
           ",[newsletter_name_remitent]"
           ",[newsletter_charset]"
           ",[newsletter_type]"
           ",[newsletter_days]"
           ",[newsletter_nb_list_to]"
           ",[newsletter_list_to]"
           ",[feed_id]"
           ",[feed_valuation_to_show]"
           ",[feed_order_by]"
           ",[feed_selection]"
           ",[feed_grouping]"
           ",[feed_feedName]"
           ",[normalized_feedName]"
           ",[feed_num_mentions])"
           " VALUES "
           "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
    
    #for newsletter in newsletters:
    #   print(newsletter)
    #    cursor.execute(stmt, newsletter)
    
    cursor.executemany(stmt, newsletters)
    conn.commit()
    conn.close()
    print('inserting {} rows into [dbo].[json.newsletters]'.format(len(newsletters)))
 
def save_all_matchings(feeds):
    serverName='.'
    databaseName='UbermetricsMigration'
    conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                'Server=' + serverName + ';'
                'Database=' + databaseName + ';'
                'Trusted_Connection=yes;')
    cursor = conn.cursor()

    stmt = """DELETE FROM [dbo].[matchings.all]"""
    cursor.execute(stmt)
    print('deleting existing entries in [dbo].[matchings.all]')

    stmt = ("INSERT INTO [dbo].[matchings.all]"
            "([folder_name]"
            ",[json_file_path]"
            ",[json_customer_id]"
            ",[json_customer_name]"
            ",[json_customer_name_normalized]"
            ",[json_feed_id]"
            ",[json_feed_name]"
            ",[json_feed_name_normalized]"
            ",[json_feed_property]"
            ",[json_feed_key]"
            ",[json_feed_format]"
            ",[json_feed_link]"
            ",[ub_login]"
            ",[ub_password]"
            ",[ub_name]"
            ",[ub_label]"
            ",[ub_type])"
            " VALUES "
            "(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    )
    
    cursor.executemany(stmt, feeds)
    conn.commit()
    conn.close()
    print('inserting {} rows into [dbo].[matching.all]'.format(len(feeds)))

def save_matchings_normalized():
    serverName='.'
    databaseName='UbermetricsMigration'
    conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                'Server=' + serverName + ';'
                'Database=' + databaseName + ';'
                'Trusted_Connection=yes;')
    cursor = conn.cursor()
    
    stmt = """DELETE FROM [dbo].[matchings_normalized]"""
    cursor.execute(stmt)
    print('deleting existing entries in [dbo].[matchings_normalized]')

    stmt = ("INSERT INTO [dbo].[matchings_normalized] "            
            "SELECT DISTINCT "
            "   ub.[json_file_path] as monitor_file_path,"
            "	ub.[json_feed_id] as monitor_feed_id,"
            "	ub.[json_feed_name] as monitor_feed_name,"
            "	ub.[json_feed_name_normalized],"
            "	ub.[json_feed_key] as monitor_feed_key,"
            "	ub.[json_customer_id] as monitor_customer_id,"
            "	ub.[json_customer_name] as monitor_customer_name, "
            "	ub.[json_customer_name_normalized],"
            "	[augure_application] = CASE "
            "							WHEN [json_customer_id] = 34563 THEN 'https://acf.hosting.augure.com/Augure_ACF'"
            "							WHEN [json_customer_id] = 36087 THEN 'https://oliviapayerne.hosting.augure.com/Augure_OP'"
            "							WHEN [json_customer_id] = 42937 THEN 'https://raoul.hosting.augure.com/Augure_Raoul'"
            "							WHEN [json_customer_id] = 41328 THEN 'https://atos.hosting.augure.com/Augure_Atos'"
            "							WHEN [json_customer_id] = 43379 THEN 'https://alima.hosting.augure.com/Augure_Alima'"
            "							WHEN [json_customer_id] = 41806 THEN 'https://versaillesagglo.hosting.augure.com/Augure_VGP'"
            "							WHEN [json_customer_id] = 41176 THEN 'https://fenwick.hosting.augure.com/Augure_Fenwick'"
            "							WHEN [json_customer_id] = 38285 THEN 'https://ideealconseil.hosting.augure.com/Augure_IdeealConseil'"
            "							WHEN [json_customer_id] = 40709 THEN 'https://terremajeure.hosting.augure.com/Augure_TerreMajeure'"
            "							WHEN [json_customer_id] = 35841 THEN 'https://sanef.hosting.augure.com/Augure_SANEF'"
            "							WHEN [json_customer_id] = 40535 THEN 'https://volvo.hosting.augure.com/Augure_Volvo'"
            "							WHEN [json_customer_id] = 39723 THEN 'https://voxco.hosting.augure.com/Augure_VoxCo'"
            "							WHEN [json_customer_id] = 32582 THEN 'https://vinci.hosting.augure.com/Augure_Vinci'"
            "							WHEN [json_customer_id] = 40087 THEN 'https://institut-montaigne.hosting.augure.com/Augure_InstitutMontaigne'"
            "							WHEN [json_customer_id] = 41214 THEN 'https://mazda.hosting.augure.com/Augure_Mazda'"
            "							WHEN [json_customer_id] = 38391 THEN 'https://fim.hosting.augure.com/Augure_FIM'"
            "							WHEN [json_customer_id] = 35426 THEN 'https://inra.hosting.augure.com/Augure_INRA'"
            "							WHEN [json_customer_id] = 37957 THEN 'https://ageas.hosting.augure.com/Augure_AGEAS'"
            "							WHEN [json_customer_id] = 40394 THEN 'https://carl-f-bucherer.hosting.augure.com/Augure_Bucherer'"
            "							WHEN [json_customer_id] = 35258 THEN 'https://versailles.hosting.augure.com/Augure_Versailles'"
            "							WHEN [json_customer_id] = 38103 THEN 'https://adami.hosting.augure.com/Augure_ADAMI'"
            "							WHEN [json_customer_id] = 37343 THEN 'https://veolia.hosting.augure.com/Augure_Veolia'"
            "							WHEN [json_customer_id] = 34698 THEN 'https://warner.hosting.augure.com/Augure_Warner'"
            "							WHEN [json_customer_id] = 40262 THEN 'https://ekibio.hosting.augure.com/Augure_Ekibio'"
            "							WHEN [json_customer_id] = 32562 THEN 'https://cnamts.hosting.augure.com/Augure_CNAMTS'"
            "							WHEN [json_customer_id] = 44408 THEN 'https://noplasticinmysea.hosting.augure.com/Augure_NPIMS'"
            "							WHEN [json_customer_id] = 30231 THEN 'https://abbvie.hosting.augure.com/Augure_Abbott'"
            "							WHEN [json_customer_id] = 35298 THEN 'https://ach.hosting.augure.com/Augure_ACH'"
            "							WHEN [json_customer_id] = 34144 THEN 'https://manosunidas.hosting.augure.com/Augure_ManosUnidas'"
            "							WHEN [json_customer_id] = 36001 THEN 'https://tragsa.hosting.augure.com/Augure_Tragsa'"
            "							WHEN [json_customer_id] = 32480 THEN 'https://philips.hosting.augure.com/Augure_Philips'"
            "							WHEN acc.[app_url] = '???' OR acc.[app_url] IS NULL OR LEN(acc.[app_url])=0 THEN NULL "
            "							ELSE acc.[app_url]"
            "							END,"
            "	ub.[ub_login],"
            "	ub.[ub_password],"
            "	ub.[ub_name],"
            "   factory = (SELECT COUNT(1) from factory_feeds where Monitor_Key=ub.json_feed_key),"
            "   newsletter = (SELECT COUNT(1) from json_newsletters where feed_id=ub.json_feed_id),"
            "   ub.[ub_label]"
            " FROM [dbo].[matchings.all] ub "
            "	LEFT JOIN [ub.accounts] acc ON acc.[login] = ub.[ub_login]")
    
    cursor.execute(stmt)
    conn.commit()
    conn.close()
    print('inserting normalized rows into [dbo].[matching_normalized]')
    
def get_normalized_matchings():
    serverName='.'
    databaseName='UbermetricsMigration'
    conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                'Server=' + serverName + ';'
                'Database=' + databaseName + ';'
                'Trusted_Connection=yes;')

    stmt = ("SELECT [monitor_file_path]"
        ",[monitor_feed_id]"
        ",[monitor_feed_name]"
        ",[monitor_feed_key]"
        ",[monitor_customer_id]"
        ",[monitor_customer_name]"
        ",[ub_login]"
        ",[ub_name]"
        ",[ub_label]"
	    ",[augure_application]"
        ",[factory]"
        ",[newsletter]"
        "FROM [UbermetricsMigration].[dbo].[matchings_normalized] ORDER BY [monitor_file_path] ASC")
    cursor = conn.cursor()
    cursor.execute(stmt)
    result = cursor.fetchall()

    print("retrieving {} matchings from the UbermetricsMigration".format(len(result)))
    return result
