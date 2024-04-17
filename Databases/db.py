import sqlite3
#https://www.youtube.com/watch?v=7lXTfS4Bbrg&list=PLjf6nsEcF5KMhk0ZmTQzzWtvoEHY84B8p&index=4
#WE DONT WANT TO HAVE MULTIPLE CONNECTIONS TO OUR DATABASE, SO WE USE SINGLETON PATTERN
def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls() #class private constructor cagiriyor
        return instances[cls]
    
    return getinstance

#use conn.commit if changes were made in database, if we just do get or select => no need to self.conn.commit
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

    def get_all_tasks(self):
        cursor = self.conn.execute(
            """

            SELECT * FROM task;
            """
        )
        tasks =[]
        for row in cursor:
            tasks.append(
                {
                    "id":row[0],
                    "description":row[1],
                    "done":bool(row[2])
                }
            )
            return tasks
        
    def insert_task_table(self,description,done):
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO task(description,done) VALUES(?,?);

            """,
            (description,done)
        )
        self.conn.commit()
        return cur.lastrowid
    
    def get_task_by_id(self,id):
        cur = self.conn.execute(
            """
            SELECT * FROM task WHERE id = ?;
            """,
            (id,) #even if we enter one parameter put , besides that like a two element tuple
        )

        for row in cur:
            return {
                "id":row[0],
                "description":row[1],
                "done":bool(row[2])
            }
        return None
    
    def update_task_by_id(self,id,description,done):
        self.conn.execute(
            """
            UPDATE task SET description=?, done=? WHERE id=?;
            """,
            (description,done,id)
        )
        self.conn.commit()

    
    def delete_task_by_id(self,id):
        self.conn.execute(
            """
            DELETE FROM task WHERE id=?;
            """,
            (id,)
        )

DatabaseDriver = singleton(DatabaseDriver) 