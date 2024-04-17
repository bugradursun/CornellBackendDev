import json
from flask import Flask
from flask import request
import sys
import db #our db.py

#print(sys.path)
#create and activate env
#py -3 -m venv .venv
#.venv\Scripts\activate

#starting development error => python -m flask run

DB = db.DatabaseDriver() #single instance of our database driver

app = Flask(__name__)

def success_response(data,code=200):
    return json.dumps({"success" : True,"data":data}),code

def failure_response(error,code=400):
    return json.dumps({"success":False,"error":error}),code


@app.route("/")
@app.route("/tasks/")
def get_tasks():
    return success_response(DB.get_all_tasks)

@app.route("/tasks/",methods=["POST"])
def create_task():
    body = json.loads(request.data)
    description = body.get("description")
    if description is not None:
        task_id = DB.insert_task_table(description,False)
        return success_response(DB.get_task_by_id(task_id))
    return failure_response("No Description",400)

@app.route("/tasks/<int:task_id>/")
def get_task(task_id):
    task = DB.get_task_by_id(task_id)
    if task is not None:
        return success_response(task)
    return failure_response("Error Task Not found!")
@app.route("/tasks/<int:task_id>/",methods=["POST"])
def update_task(task_id):
    body = json.loads(request.data)
    description=body.get("description")
    done = body.get("done")

    task=DB.get_task_by_id(task_id)
    if description is None and done is None:
        return failure_response("Not enough information",400)
    elif description is None:
        DB.update_task_by_id(task_id,task['description'],done)
    elif done is None:
        DB.update_task_by_id(task_id,description,task['done'])
    else:
        DB.update_task_by_id(task_id,description,done)

    return success_response(DB.get_task_by_id(task_id))

@app.route("/tasks/<int:task_id>/",methods=["DELETE"])
def delete_task(task_id):
    task  = DB.get_task_by_id(task_id)
    if task is None:
        return failure_response("Task not found!")
    DB.delete_task_by_id(task_id)
    return success_response(task)


if __name__ == "__main__":
    app.run(debug=True)  # Runs the Flask development server
