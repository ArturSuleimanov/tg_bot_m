# run this file to create db
import os

from models.database import DATABASE_NAME
from models import create_database as db_creator

if __name__ == '__main__':
    db_is_created = os.path.exists(DATABASE_NAME)   # checking if db exists
    if not db_is_created:
        db_creator.create_database()    # creating db
