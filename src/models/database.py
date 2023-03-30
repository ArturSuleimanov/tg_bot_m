from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_NAME = 'bot.sqlite'    # name of our db
ENGINE_NAME = f'sqlite:///{DATABASE_NAME}' if "model" in os.getcwd() else f'sqlite:///models{os.path.join(os.sep, DATABASE_NAME)}'
engine = create_engine(ENGINE_NAME)    # setting db engine
Session = sessionmaker(bind=engine)     # creating our db session object to make db requests
Base = declarative_base()   # need our entities to be implemented from this to let sqlalchemy know it should create such table



def create_db():
    # run this to create db
    Base.metadata.create_all(engine)