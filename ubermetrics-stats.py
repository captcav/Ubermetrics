# coding=utf-8
import os
import json
import api
import csv
import sys
import datetime
import pickle
import commons
from  matching import Tree
from ubermetricsConn import UbermetricsConn
from dotenv import load_dotenv
load_dotenv()

def search_mentions(searchId, startDate, endDate, offset, limit, conn):
    params = {
        "searches.id":searchId,
        "created.geq":startDate,
        "created.leq":endDate,
        "sort":"created:asc",
        "limit":limit,
        "offset":offset * limit
    }
    try:
        response = conn.search(params)
    except Exception as ex:
        print("Error: {0}".format(ex) )

    items = []
    total = response["total"]
    maxPublishedDate = datetime.datetime.min
    for item in response["items"]:
        currentPublishedDate = datetime.datetime.strptime(item["document"]["published"], '%Y-%m-%dT%H:%M:%S.%fZ')
        if currentPublishedDate > maxPublishedDate:
            maxPublishedDate = currentPublishedDate
        items.append(item)

    return {
        "total": total,
        "startDate": startDate,
        "endDate": endDate,
        "maxPublishedDate":maxPublishedDate,
        "items":items
    }

def formatDate(value:str):
    return value[:19]

def get_mentions(login, password, searchId, startDate, endDate):
    conn = UbermetricsConn (login, password)
    params = {
        "searches.id":searchId,
        "created.geq": startDate,
        "created.leq": endDate,
        "sort":"created:desc",
        "limit":1
    }
    response = conn.search(params)
    total = response["total"]
    print("login: {0} | search.id: {1} | nb mentions: {2}".format(login, searchId, total))

    offset = 0
    limit = 100
    all_items = []

    result = {
        "total":total, 
        "startDate":startDate,
        "endDate":endDate,
        "maxPublishedDate":datetime.datetime.min,
        "items":[]
    }
    items = None
    while (items is None or len(items)==100 ):
        if offset == 100:
            conn.userId = None
            offset = 0
            total = result["total"]
            startDate = result["maxPublishedDate"].strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        result = search_mentions(searchId, startDate, endDate, offset, limit, conn)
        items = result["items"]
        all_items = all_items + items
        print("{0} -> retrieved {6} mentions ({1}/{2}) | startDate:{3} | endDate:{4} | maxPublishedDate:{5}".format(offset, len(all_items), result['total'], formatDate(result['startDate']), formatDate(result['endDate']), result['maxPublishedDate'], len(items)))
        offset +=1
    
    filename = "{0}.{1}.pickle".format(login, searchId)
    print('save {0} mentions from search.id={1} from {2} to {3} in {4}'.format(len(all_items), searchId, startDate, endDate, filename))
    pickle.dump(all_items, open(filename, "wb" ))

def get_counts(contract, startDate, endDate, augure_connection):
    total_piges = api.get_piges_count(contract, startDate, endDate, augure_connection)

    login = contract["factory"]["SourceConnectionUserName"]
    password = contract["factory"]["SourceConnectionPassword"]
    searchId = contract["factory"]["Search_ID"]
    nextIntegrationParameter = contract['factory']['NextIntegrationParameter']
    nextIntegrationParameter_toDateTime = commons.convert_dotnet_tick(nextIntegrationParameter)
    total_mentions = -1
    diff_mentions_piges = -1
    message = None

    try:
        conn = UbermetricsConn (login, password)
        params = {
            "searches.id":searchId,
            "created.geq": startDate,
            "created.leq": endDate,
            "sort":"created:desc",
            "limit":1
        }
        response = conn.search(params)
        total_mentions = response["total"]
        diff_mentions_piges = total_mentions-total_piges
    except Exception as ex:
        message = str(ex)

    return [
        contract['factory']['ApplicationUrl'],
        contract['factory']['Destination_Path'],
        contract['augure']['CodeContrat'],
        login,
        searchId,
        total_mentions,
        total_piges, 
        diff_mentions_piges,
        nextIntegrationParameter_toDateTime,
        str(nextIntegrationParameter),
        message
    ]

def get_missing_mentions(items:list, mentions:list):
    missings = []
    for mention in mentions:
        mentionId = mention["uuid"]
        found = len(list(filter(lambda x: x[0] == mentionId, items))) > 0
        if found == False:
            missings.append(mention)
    return missings

def ubermetric_vs_augure(applications, startDate, endDate):
    error = []
    results = [["Application", "Feed", "Augure Contract ID", "UM account", "UM Search ID", "Nb UBERMETRICS", "Nb AUGURE", "Delay", "Last integration date", "NextIntegrationParameter", "Message"]]
    counter = 0

    for application in applications[1:]:
        counter=counter+1
        print("{0}. application {1}".format(counter, application[0]))
        try:
            url = application[0]
            backend = application[1]
            database=commons.get_database_name(url)
            username = os.getenv("SQL_USERID")
            password = os.getenv("SQL_PASSWORD")
            augure_connection = "Driver={{ODBC Driver 17 for SQL Server}};Server={0}.hosting.augure.com;Database={1};UID={2};PWD={3}".format(backend, database, username, password)
            contracts = api.get_all_feeds(augure_connection)
            for contract in contracts:
                print("  contract:{0} | factory login:{2} | factory search ID:{3} | factory feed:{1}".format(contract['augure']['CodeContrat'], contract['factory']['Destination_Path'], contract['factory']['SourceConnectionUserName'], contract['factory']['Search_ID']))
                results.append(get_counts(contract, startDate, endDate, augure_connection))
        except Exception as e:
            error.append({
                "application": application[0],
                "message": str(e)
            })
    return results

try:
    action = sys.argv[1]
    if sys.argv[1] == '-um-vs-aug':
        startDate = sys.argv[2] #"2021-01-01T00:00:00Z"
        endDate = sys.argv[3] #"2021-01-26T23:59:00Z"
        sheetname = sys.argv[4]
        applications = api.get_augure_applications()
        result = ubermetric_vs_augure(applications, startDate, endDate)
        api.export_um_augure_to_google(result, '1GNKGDSH9B_Isf9Q8KfWDwvjVv2FmciaNp3wB38sSyLY', sheetname)
    elif sys.argv[1] == '-search':
        startDate = "2021-01-01T00:00:00Z"
        endDate = "2021-01-22T23:59:00Z"
        login = sys.argv[2]
        password = sys.argv[3]
        searchId = sys.argv[4]
        get_mentions(login, password, searchId, startDate, endDate)
    elif sys.argv[1] == '-compare':
        pickle_file = sys.argv[2]
        customer_file_id=sys.argv[3]
        codeContract = sys.argv[4]
        mentions = pickle.load(open(pickle_file, "rb" ))
        print("{0} mentions loaded from Ubermetric cache {1}".format(len(mentions), pickle_file))
        customerId = api.get_customer_ID(customer_file_id)
        #clips = api.get_sourceIDs(customerId)
        piges = api.get_pigeIDs(codeContract, '2021-01-01 00:00', '2021-01-21 23:59')
        missings = get_missing_mentions(piges, mentions)
        print("{} mention not found".format(len(missings)))
       
        for item in missings[:100]:
            try:
                doc_id = item["document"]["id"]
                print("{0} | created={1} | published={2} | doc.id={3} | {4}".format(item["uuid"], item["created"], item["document"]["published"], doc_id, str(item["document"]["title"])[:30]))
            except Exception as e:
                print("{0} | created={1} | published={2} | doc.id={3} | {4}".format(item["uuid"], item["created"], item["document"]["published"], item["document"]["id"], "ERROR: " + str(e)))
    elif sys.argv[1] == '-client':
        backend = sys.argv[2]
        databaseName = sys.argv[3]
        startDate = sys.argv[4]     #"2021-01-01T00:00:00Z"
        endDate = sys.argv[5]       #"2021-01-27T23:59:00Z"
        connection_string = "Driver={{ODBC Driver 17 for SQL Server}};Server={0}.hosting.augure.com;Database={1};UID={2};PWD={3}".format(backend, databaseName, os.getenv("SQL_USERID"), os.getenv("SQL_PASSWORD"))
        feeds = api.get_all_feeds(connection_string)
        results = []
        for contract in feeds:
                print("  contract:{0} | factory login:{2} | factory search ID:{3} | factory feed:{1}".format(contract['augure']['CodeContrat'], contract['factory']['Destination_Path'], contract['factory']['SourceConnectionUserName'], contract['factory']['Search_ID']))
                results.append(get_counts(contract, startDate, endDate, connection_string))
        for r in results:
            print(r)
    else:
        raise Exception("action undefined: " + sys.argv[1]) 
except Exception as ex:
    print(ex)
    print("usage: python ubermetrics.py <action> [options]")
    