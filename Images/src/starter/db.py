from flask_sqlalchemy import SQLAlchemy
import base64
import boto3 #for AWS
import datetime
from io import BytesIO #convert to byrestring base64 string to bytesstring to pass to aws
from mimetypes import guess_extension,guess_type #images/png => guess_extension => .png output (since we want to use other .png,.gif ..)
import os
from PIL import Image
import random
import re
import string

db = SQLAlchemy()

EXTENSIONS = ['png','gif','jpg','jpeg']
BASE_DIR = os.getcwd() #current path
S3_BUCKET = 'bugrademo8' #amazon s3 bucket name
S3_BASE_URL = f'https://{S3_BUCKET}.s3-eu-north-1.amazonaws.com'

class Asset(db.Model):
    __tablename__ = 'asset'

    id = db.Column(db.Integer,primary_key = True)
    base_url = db.Column(db.String,nullable=False)
    salt = db.Column(db.String,nullable=False) #security purpose
    extension = db.Column(db.String,nullable=False)
    height =db.Column(db.Integer,nullable=False)
    width = db.Column(db.Integer,nullable=False)
    created_at = db.Column(db.DateTime,nullable=False)

    def __init__(self,**kwargs):
        self.create(kwargs.get('image_data')) 

    def serialize(self):
        return{
            "url":f"{self.base_url}/{self.salt}.{self.extension}",
            "created_at":str(self.created_at)
        }
    
    def create(self,image_data):
        try:
            ext = guess_extension(guess_type(image_data)[0])[1:] #take the first element,slice from 1 index to end which gives us 'png' or 'gif' etc..
            if ext not in EXTENSIONS : 
                raise Exception(f'Extension {ext} not supported!')
            
            salt = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for i in range(16))
        except Exception as e:
            print('Error:',e)