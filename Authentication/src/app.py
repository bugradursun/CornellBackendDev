import json

from db import db
from flask import Flask,request

db_filename = "auth.db"
app=Flask(__name__)

app.config["SQL_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app) #to initialize db, must use this
with app.app_context():
    db.create_all()

def success_response(data,code=200):
    return json.dumps(data),code

def failure_response(message,code=400):
    return json.dumps({"error" : message}), code

def extract_token(request):
    """
    Helper function that extracts the token from the header of the request
    """
    auth_header = request.headers.get("Authorization")
    if auth_header is None:
        return False,json.dumps({"error:Missing auth header"})
    bearer_token = auth_header.replace("Bearer ","").strip() #just the token part is extracted
    if bearer_token is None or not bearer_token:
        return False,json.dumps({"error":"Invalid auth header"})

@app.route("/")
def hello_world():
    return json.dumps({"message":"Hello,World!"})