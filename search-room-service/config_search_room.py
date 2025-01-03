'''
Файл конфігурацій проєкту
'''

import os
from dotenv import load_dotenv
class Config:
    load_dotenv()
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI_PROFILE')
    SQLALCHEMY_TRACK_MODIFICATIONS = False