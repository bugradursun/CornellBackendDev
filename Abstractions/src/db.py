from flask_sqlalchemy import SQLAlchemy # type: ignore
#https://backend-course.cornellappdev.com/chapters/abstractions/demo
db = SQLAlchemy()

# implement database model classes

association_table = db.Table(
    'association',
    db.Column('task_id',db.Integer,db.ForeignKey('task.id')),
    db.Column('category_id',db.Integer,db.ForeignKey('category.id'))
)

class Task(db.Model):
    __tablename__='task'
    id = db.Column(db.Integer,primary_key = True)
    description = db.Column(db.String,nullable=False)
    done = db.Column(db.Boolean,nullable = False)
    subtasks = db.relationship('Subtask',cascade='delete')
    categories = db.relationship('Category',secondary = association_table,back_populates = 'tasks')

    def __init__(self,**kwargs):
        self.description = kwargs.get('desription')
        self.done =kwargs.get('done')

    def serialize(self):
        return{
            "id":self.id,
            "description":self.description,
            "done":self.done,
            "subtasks": [s.serialize() for s in subtasks], ##error?
            "categories" : [c.serialize() for c in categories]

        }
    
class Subtask(db.Model):
    __tablename__ = 'subtask'
    id=db.Column(db.Integer,primary_key= True)
    description = db.Column(db.String,nullable=False)
    done=db.Column(db.Boolean,nullable=False)
    task_id = db.Column(db.Integer,db.ForeignKey('task.id')) ##we are referencing to table task, column id

    def __init__(self,**kwargs):
        self.description = kwargs.get('description')
        self.done = kwargs.get('done')
        self.task_id=kwargs.get('task_id')
    
    def serialize(self):
        return {
            "id":self.id,
            "description":self.description,
            "done":self.done,
        }
    
class Category(db.Model):
    __tablename__ = 'category'
    id=db.Column(db.Integer,primary_key=True)
    description=db.Column(db.String,nullable=False)
    color = db.Column(db.String,nullable=False)
    tasks = db.relationship('Task',secondary=association_table,back_populates = 'categories')

    def __init__(self,**kwargs):
        self.description = kwargs.get('description')
        self.done = kwargs.get('done')
        self.color=kwargs.get('color')

    def serialize(self) :
        return {
            "id":self.id,
            "description":self.description,
            "color":self.color
        }