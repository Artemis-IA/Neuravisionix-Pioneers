from flask import Flask
from flask_pymongo import PyMongo
import os
def scan_folder():
    folder_path = 'image_server/'
    image_files = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                image_path = os.path.join(root, file)
                image_files.append({'name': file, 'path': image_path, 'labels':False})
    return image_files


# def scan_folder():
#     folder_path = '../image_server/' 
#     print("folder: ",folder_path)
#     for root, dirs, files in os.walk(folder_path): 
#             for file in files:
#                 if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
#                     image_path = os.path.join(root, file)
                    
#                     # Vérifier si l'image existe déjà dans la base de données
#                     existing_image = mongo.db.images.find_one({'name': file, 'path': image_path})
#                     if existing_image is None:
#                         image_files.append({'name': file, 'path': image_path})




