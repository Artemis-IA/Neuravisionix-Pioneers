from os import environ

class Config:
    SECRET_KEY = 'jkdbvlqdfvqldvihviviuqvisdhfv'  # Change this to a strong, random secret key
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{environ.get("MYSQL_USER")}:{environ.get("MYSQL_PASSWORD")}@{environ.get("MYSQL_HOST")}/{environ.get("MYSQL_DATABASE")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
