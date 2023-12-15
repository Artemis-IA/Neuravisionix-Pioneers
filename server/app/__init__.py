from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo 
from os import environ
app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)
app.config['MONGO_URI'] = f'mongodb://{environ.get("MONGO_INITDB_ROOT_USERNAME")}:{environ.get("MONGO_INITDB_ROOT_PASSWORD")}@{environ.get("MONGO_INITDB_HOST")}/{environ.get("MONGO_INITDB_DATABASE")}?authSource=admin'  
mongo = PyMongo(app)
from app import routes, models
 