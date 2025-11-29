import os

class Config:
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 5000))
    DEBUG = False