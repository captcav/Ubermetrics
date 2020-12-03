import unidecode
import os

def get_prop(property, obj):
    if property in obj:
        return obj[property]
    else:
        return None

def join_prop(property, obj, sep):
    if property in obj:
        values = obj[property]
        if values is None: 
            return None
        else:
            return sep.join(values)
    else:
        return None

def normalized(s):
    if s is not None:
        s_diacritics_removed = unidecode.unidecode(s)
        return s_diacritics_removed.translate ({ord(c): "" for c in " '""!@#$%^&*()[]{};:,./<>?\\|`~-=_+"}).lower().capitalize()
    return s

def get_folder_name(folder_path): 
    parts = folder_path.split('\\')
    return parts[len(parts)-1]

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
