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

#example : lets have a row = (1,"Task Description",0) and ["id","description","done"] as column
#output will be like this : {"id":1,"description":"Task description","done":0}
def parse_row(row,columns):
    parsed_row = {}
    for i in range(len(columns)):
        parsed_row[columns[i]] = row[i]
    return parsed_row

#cursor stores the result of a query from a database,
#lets have cursor = [
#    (1, "Task 1", 0),
#    (2, "Task 2", 1),
#    (3, "Task 3", 0)
#]
#output will be like: [{"id":1,"description":"Task 1","done":0} , {"id":2,"description":"Task 2 ","done": 1}, ....]
def parse_cursor(cursor,columns):
    return [parse_row(row,columns) for row in cursor]


#use conn.commit if changes were made in database, if we just do get or select => no need to self.conn.commit
class DatabaseDriver(object):
    #Database driver for the task app
    #Handles reading and writing data with the database.

    def __init__(self) : ##constructor
        self.conn = sqlite3.connect('todo.db',check_same_thread=False) #since we will use singlethread, second argument can be false.No multithread, no possible conflicts
        self.create_task_table()
        self.create_subtask_table()
        self.conn.commit()
    
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
        tasks = parse_cursor(cursor,["id","description","done"])
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
            return parse_row(row,["id","description","done"])
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

#--SUBBTASKS---------------------------------
    
    def create_subtask_table(self):
        try:
            self.conn.execute(
                """
                CREATE TABLE subtask(
                id INTEGER PRIMARY KEY,
                description TEXT NOT NULL,
                done BOOLEAN NOT NULL,
                task_id INTEGER NOT NULL,
                FOREIGN KEY (task_id) REFERENCES task(id)
                );
                """
            )
            self.conn.commit()
            print("subtask table created successfully!")
        except Exception as e:
            print(f"Error createing subtask table: {e}")

    def get_all_subtasks(self) : 
        cursor = self.conn.execute("SELECT * FROM subtask;")
        subtasks = parse_cursor(cursor,["id","description","done","task_id"])
        return subtasks
    
    def insert_subtask(self,description,done,id):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO subtask (description,done,task_id) VALUES (?,?,?);" , (description,done,id)) ##error ?
        self.conn.commit()
        return cursor.lastrowid
    
    def get_subtask_by_id(self,id):
        cursor = self.conn.execute("SELECT * FROM subtask WHERE id = ?;",(id,))
        for row in cursor : 
            return parse_row(row,["id","description","done","task_id"])
        return None
    
    def get_subtasks_of_task(self,id):
        cursor = self.conn.execute("SELECT * FROM subtask WHERE task_id = ?;",(id,))
        subtasks = parse_cursor(cursor,["id","description","done","task_id"])
        return subtasks
        
 


DatabaseDriver = singleton(DatabaseDriver) 