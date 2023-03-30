# !!! don't remove this imports, we need them to create such tables in db

from models.database import create_db, Session
from models.question import Question
from models.service import Service
from models.user import User

def create_database():
    create_db()
