import sqlite3

def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls() #class private constructor cagiriyor
        return instances[cls]
    
    return getinstance

class DatabaseDriver(object):
    #Database driver for the task app
    #Handles reading and writing data with the database.

    def __init__(self) :
        self.conn = sqlite3.connect('todo.db',check_same_thread=False) #since we will use singlethread, second argument can be false.No multithread, no possible conflicts
        self.create_task_table()
    
    def create_task_table(self):
        try:
            self.conn.execute(
                """
                CREATE TABLE task (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                done INTEGER NOT NULL
                );
                """
            )
            self.conn.commit()
        except Exception as e:
            print(e)

    def delete_task_table(self):
            self.conn.execute(
                """
                DROP TABLE IF EXISTS task;
                """     
            )
            self.conn.commit() # ?