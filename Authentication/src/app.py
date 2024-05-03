import json

from db import User, db
from flask import Flask,request

db_filename = "auth.db"
app=Flask(__name__)

app.config["SQL_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app) #to initialize db, must use this
with app.app_context():
    db.create_all()
#GETTERS
def get_user_by_email(email):
    return User.query.filter(User.email == email).first()

def get_user_by_session_token(session_token):
    return User.query.filter(User.session_token == session_token).first()

def get_user_by_update_token(update_token):
    return User.query.filter(User.update_token == update_token).first()

#RESPONSES
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
    
    return True, bearer_token
def get_user_by_email(email):
    pass

@app.route("/")
def hello_world():
    return json.dumps({"message":"Hello,World!"})

@app.route("/register/",methods=["POST"])
def register_account():
    body = json.loads(request.data)
    email = body.get("email")
    password = body.get("password")

    if email is None or password is None:
        return json.dumps({"error":"Invalid email or password"})
    
    optional_user = get_user_by_email(email) #if user is already registered

    if optional_user is not None:
        return json.dumps({"error" : "User already exists"})

    user = User(email=email,password=password)
    #is user does not exist in database,enroll => add it to db
    db.session.add(user)
    db.session.commit()

    return json.dumps(
        {
            "session_token":user.session_token,
            "session_expiration":str(user.session_expiration),
            "update_token":user.update_token,
        }
    )

@app.route("/login",methods = ["POST"])
def login():
    body = json.loads(request.data)
    email = body.get("email")
    password = body.get("password")

    if email is None or password is None : 
        return failure_response("Invalid email or password")
    
    user = get_user_by_email(email)

    success = user is not None and user.verify_password(password)

    if not success:
        return failure_response("Incorrect email or password")
    
    return json.dumps(
        {
            "session_token":user.session_token,
            "session_expiration":str(user.session_expiration),
            "update_token" : user.update_token,
        }
    )

@app.route("/session/",methods=["POST"])
def update_session():
    success,update_token = extract_token(request)

    if not success:
        return update_token
    
    user = get_user_by_update_token(update_token)

    if user is None:
        return failure_response("Error invalid update token")
    
    user.renew_session()
    db.session.commit()

    return json.dumps(
        {
            "session_token":user.session_token,
            "session_expiration":str(user.session_expiration),
            "update_token" : user.update_token,
        }
    )

@app.route("/secret/", methods = ["GET"])
def secret_message():
     success,session_token = extract_token(request)

     if not success:
         return session_token
     
     user = get_user_by_session_token(session_token)
     if not user or not user.verify_session_token(session_token):
         return failure_response("Invalid session token")
     
     return success_response("You have successfully implemented sessions")

if __name__ == "__main__":
    app.run(host = "0.0.0.0",port=8000,debug = True)