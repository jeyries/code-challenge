
import os
import datetime
import uuid
import bcrypt

from peewee import SqliteDatabase, Model
from peewee import CharField, ForeignKeyField, IntegerField, DateTimeField

ROOT = os.path.expanduser("~/.challenge")
DATABASE = os.path.join(ROOT, 'server.db')

db = SqliteDatabase(DATABASE)

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    uuid = CharField(unique=True)
    email = CharField(unique=True)
    hashed = CharField()
    score = IntegerField(default=0)
    duration = IntegerField(default=0)

    def password_set(self, password):
        # Hash a password for the first time, with a randomly-generated salt
        self.hashed = bcrypt.hashpw(password, bcrypt.gensalt())

    def password_check(self, password):
        # Check that an unencrypted password matches one that has
        # previously been hashed
        return bcrypt.hashpw(password, self.hashed) == self.hashed

    def __repr__( self ):
        return 'User %s %s' % (self.uuid, self.email)

    @property
    def json(self):
        return {
            'uuid': self.uuid,
            'email': self.email,
            'tasks': [{
                'uuid': task.uuid,
                'state': task.state,
                'created_date': str(task.created_date),
            } for task in self.tasks],
            'records': [record.json for record in self.records],
        }

    def solve(self, score, duration):
        self.score += score
        self.duration += duration
        self.save()

############


def read_file( path ): 
    if os.path.isfile(path):
        with open(path, "rt") as f:
            return f.read()

def write_file( path, data ):
    folder = os.path.dirname(path)
    if not os.path.isdir(folder):
        os.makedirs(folder)
    with open(path, "wt") as f:
        f.write(data)
        
def isoformat(d):
    if d is None:
        return None
    return d.isoformat()

class Task(BaseModel):
    uuid = CharField(unique=True)
    user = ForeignKeyField(User, related_name='tasks')
    state = CharField()
    challenge = CharField()
    now = IntegerField(default=0)
    max = IntegerField(default=0)
    created_date = DateTimeField(default=datetime.datetime.now)

    def __repr__( self ):
        return 'Task %s %s %s' % (self.uuid, self.user.email, self.state)

    @property
    def folder( self ):
        return os.path.join(ROOT, "task", self.uuid)

    @property
    def meta( self ):
        return os.path.join(self.folder, "meta.json")

    @property
    def answer( self ):
        return os.path.join(self.folder, "answer.txt")

    @property
    def stdin( self ):
        return os.path.join(self.folder, "stdin.txt")

    @property
    def stdout( self ):
        return os.path.join(self.folder, "stdout.txt")

    @property
    def stderr( self ):
        return os.path.join(self.folder, "stderr.txt")

    @property
    def result( self ):
        return os.path.join(self.folder, "result.txt")

    @property
    def json(self):
        return {
            'uuid': self.uuid,
            'user': {
                'email': self.user.email,
                'uuid': self.user.uuid,
            },
            'state': self.state,
            'challenge': self.challenge,
            'now': self.now,
            'max': self.max,
            'created_date': isoformat(self.created_date),
            'result': read_file(self.result),
        }


class Record(BaseModel):
    uuid = CharField(unique=True)
    user = ForeignKeyField(User, related_name='records')
    state = CharField()
    challenge = CharField()
    created_date = DateTimeField(default=datetime.datetime.now)
    started_date = DateTimeField(null=True)
    solved_date = DateTimeField(null=True)
    score = IntegerField(default=0)
    duration = IntegerField(default=0)

    def __repr__( self ):
        return 'Record %s %s %s' % (self.uuid, self.user.email, self.state)
    
    @property
    def json(self):
        return {
            'uuid': self.uuid,
            'state': self.state,
            'challenge': self.challenge,
            'created_date': isoformat(self.created_date),
            'started_date': isoformat(self.started_date),
            'solved_date': isoformat(self.solved_date),
            'score': self.score,
            'duration': self.duration,
        }

    def start(self):
        if self.started_date is None:
            self.started_date = datetime.datetime.now()
            self.save()

    def solve(self, score=1):
        if self.state == "done":
            return
            
        self.state = "done"
        self.solved_date = datetime.datetime.now()
        self.score = score
        delta = self.solved_date - self.started_date
        self.duration = int(delta.total_seconds())
        self.save()

        self.user.solve( score=self.score, duration=self.duration )
        

##### Challenge


class Challenge(object):

    def __init__(self, info):
        self.identifier = info['identifier']
        self.path = info['path']
        self.title = info['title']
        self.comment = info['comment']
        self.max = self.compute_max()

    @property
    def folder( self ):
        return os.path.join(ROOT, "content", self.path)

    @property
    def readme( self ):
        return os.path.join(self.folder, "readme.md")

    @property
    def json(self):
        return {
            'identifier': self.identifier,
            'path': self.path,
            'title': self.title,
            'comment': self.comment,
            'max': self.max,
        }

    def compute_max(self):
        names = set(os.listdir(self.folder))
        step = 0
        while True:
            step += 1
            name = "input%d.txt" % step
            if not name in names:
                return step - 1


##### utilities

def get_without_failing(Model, query):
    results = Model.select().where(query).limit(1)
    return results[0] if len(results) > 0 else None

