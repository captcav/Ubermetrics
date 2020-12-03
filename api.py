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
    folder_name = commons.get_folder_name(folder_path)
    ub_accounts = list(get_ub_active_accounts(isAPI))
    sf_apps = get_sf_applications()
    
    results = []
    info = process_account(folder_name, folder_path, ub_accounts, sf_apps)
    results.append(info)
    return results

def process_account(folder_name:str, folder_path:str, ub_accounts:list, sf_apps:list):

        # guess Publisher application URL 
        application_url = []
        if folder_name == 'marco':
            application_url.append("http://marcodecomunicacion.hosting.augure.com/Augure_MdCom")
        elif folder_name == 'demo_agency':
            application_url.append('https://demo.hosting.augure.com/Demo_Agencia')
        elif folder_name == 'certina' or folder_name == 'rado' or folder_name == 'swatch':
            application_url.append('http://mra.hosting.augure.com/Augure_MRA')   
        elif folder_name == 'mayoral':
            application_url.append('http://ra.hosting.augure.com/Augure_RA')   
        elif folder_name == 'elanedelman':
            application_url.append('http://agenceee.hosting.augure.com/Augure_EE')
        elif folder_name == 'oxfaminternational':
            application_url.append('http://intermonoxfam.hosting.augure.com/Augure_IntermonOxfam')            
        # elif folder == 'mapfre':
        #     application_url.append("http://mapfre.hosting.augure.com/Augure_Mapfre")
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
        	"   AND C.Customer_Name not like ('Imente_MRA_Glashutte%')"
        	"   AND C.Customer_Name not like ('Imente_Artelier_Frinsa%')"
        	"   AND C.Customer_Name not like ('Augure_SC_SerenaCapital%')"
        	"   AND (CF.Source_Path not like '%TNUMwYVhbpHyC1499hLHg%' AND CF.Source_Path not like '%89OUIOT1aNoiaOzgwc3Z3.%' AND CF.Source_Path not like '%hUMGarN5saOGVMdY0nFBl%' AND CF.Source_Path not like '%qqmZ45uOR6PKMn6A8bjCl%' AND CF.Source_Path not like '%8.IiIU0QnNtiwkkyJmnsz%' AND CF.Source_Path not like '%vMPdTxFkHFk33OtRyZiO1%' AND CF.Source_Path not like '%VcpTfxgmjLWDLtx1ET3W31%' AND CF.Source_Path not like '%P5CGVMY6ttVr9TsbetXN4%' AND CF.Source_Path not like '%1S31uLsX1M44P8ubj8Sfj0%' AND CF.Source_Path not like '%4nQGMTr4Jn4DJAUBEczVl.%') " #exclude Imente_MRA
        	"   AND (CF.Source_Path not like '%Km2JJoZLO6ZKX8DNCh53I1%' AND CF.Source_Path not like '%G9eVA5cFUc3fYcX5wcC9Q1%' AND CF.Source_Path not like '%1lIsVO.Njk5z8hLg2EbVv0%' AND CF.Source_Path not like '%adb0nEeCcD0d8aPscl6tF0%' AND CF.Source_Path not like '%P6XmeoV2PSg27Mz1xkmjU0%' AND CF.Source_Path not like '%Rs4RWTqKCVVW8xX3Ocq40%' AND CF.Source_Path not like '%02f3FKpgQG0AArsAR7Tmv1%' AND CF.Source_Path not like '%W5DYza6TcoEu.sX2y1NbX.%' AND CF.Source_Path not like '%Zx7GtSDHm3NF5swoQudL7.%' AND CF.Source_Path not like '%JL9n2gCILnefWsYMDKyU0%' AND CF.Source_Path not like '%rnTE9UAjvm1yiH1.AYPl.0%' AND CF.Source_Path not like '%Hol.nCIM9.WAG8w.GInuF%' AND CF.Source_Path not like '%3.4manlLkmtij.rAWjURj.%' AND CF.Source_Path not like '%kxdKm4Tbi8gr9dw5nGgih0%') " #exclude DEVA
        	"   AND (CF.Source_Path not like '%WWlJsLSAqR1DVmRbRh.GT.%' AND CF.Source_Path not like '%88Cbc2FVgKX662TqNatd.%' AND CF.Source_Path not like '%DcoEWKOXIR6YXoFDznQt%') " #exclude Endesa
        	"   AND (CF.Source_Path not like '%ZWfTE0KeFzOmRskQqheo.%') " #exclude Imente_Artelier_LaboratoriosQuinton
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
    stmt = """DELETE FROM dbo.[json_newsletters]"""
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
    
    cursor.executemany(stmt, newsletters)
    conn.commit()
    conn.close()
    print('deleting existing entries and inserting {} new entries into dbo.[json.newsletters]'.format(len(newsletters)))
 

