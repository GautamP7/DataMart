import os

class Config(object):
    # SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    MYSQL_DATABASE_USER = 'root'
    MYSQL_DATABASE_PASSWORD = 'dm1234'
    MYSQL_DATABASE_DB = 'DataMarket'
    MYSQL_DATABASE_HOST = 'localhost'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:dm1234@localhost/DataMarket'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    MAX_CONTENT_LENGTH = 1024 * 1024 * 1024
    WHOOSH_BASE = '/var/www/html/dm/app/whoosh' 
