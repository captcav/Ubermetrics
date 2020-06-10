def get_folder_name(folder_path): 
    parts = folder_path.split('\\')
    return parts[len(parts)-1]
