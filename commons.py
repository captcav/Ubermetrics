import unidecode
import os
import csv

def get_prop(property, obj):
    if property in obj:
        return obj[property]
    else:
        return ''

def join_prop(property, obj, sep):
    if property in obj:
        values = obj[property]
        if values is None: 
            return ''
        else:
            return sep.join(values)
    else:
        return ''

def var_to_sql(s):
    if s is None:
        s=''
    return s if len(s) > 0 else None

def normalized(s):
    if s is not None:
        s_diacritics_removed = unidecode.unidecode(s)
        return s_diacritics_removed.translate ({ord(c): "" for c in " '""!@#$%^&*()[]{};:,./<>?\\|`~-=_+"}).lower().capitalize()
    return s

def get_folder_name(path): 
    if path is None:
        return None

    parts = path.split('\\')
    if os.path.isdir(path):
        return parts[len(parts)-1]
    elif os.path.isfile(path):
        return parts[len(parts)-2]

def get_json_filepath(folder):   
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

def extract_csv_to_tuples(filepath:str, sep:str):
    if not os.path.isfile(filepath):
        print("{} not found".format(filepath))
    
    data = []
    with open(filepath, newline='') as csvfile:
        data=[tuple(line) for line in csv.reader(csvfile,delimiter=';')]
    return data
    