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
        """
        Given an image in base64 encoding,does the following:
        1.Reject image if not supported filename
        2.Generate a random string for the image filename
        3.Decodes the image and attemps to upload AWS
        
        """
        try:
            ext = guess_extension(guess_type(image_data)[0])[1:] #take the first element,slice from 1 index to end which gives us 'png' or 'gif' etc..

            if ext not in EXTENSIONS : 
                raise Exception(f'Extension {ext} not supported!')
            
            salt = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for i in range(16)) #random string is generated 

            img_str = re.sub("^data:image/.+base64,","",image_data) #1)looking for data:image/ => 2) . means go to the end, + ; means go until ;base64. , and replace it with "",take from image_data
            img_data = base64.b64decode(img_str)
            img = Image.open(BytesIO(img_data))

            self.base_url = S3_BASE_URL
            self.salt = salt 
            self.extension =ext
            self.height = img.height
            self.width = img.width
            self.created_at = datetime.datetime.now()

            img_filename = f'{salt}.{ext}'
            self.upload(img,img_filename)

        except Exception as e:
            print('Error:',e)

    def upload(self,img,img_filename):
        """
        Upload the image into S3 bucket
        """

        try:
            img_temploc =f'{BASE_DIR}/{img_filename}'
            img.save(img_temploc)

            #upload image into S3 bucket
            s3_client = boto3.client("s3") #aws connection
            s3_client.upload_file(img_temploc,S3_BUCKET,img_filename)

            s3_resource = boto3.resource("s3") #resource for s3
            object_acl = s3_resource.ObjectACL(S3_BUCKET,img_filename)
            object_acl.put(ACL ="public-read") #now anybody can read our image url

            #remove img from temp loc
            os.remove(img_temploc)

        except Exception as e:
            print('Error while uploading',e)