import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from models.database import *
from aiogram import types

from config import SUPPORT_DELAY


class User(Base):
    # user table description

    __tablename__ = 'user'


    id = Column(Integer, primary_key=True)
    tg_name = Column(String(55))
    last_supported = Column(DateTime)
    can_be_supporte = Column(Boolean, default=False, nullable=False)    # sqlite has length limit on column name



    def __init__(self, id: int, tg_name: str) -> None:
        self.id = id
        self.tg_name = tg_name


    @classmethod
    def add_user(cls, msg: types.Message):
        # adds user or updates if exists
        with Session() as session:
            user_from_db = session.query(User).get(msg.from_user.id)
            if user_from_db:
                session.query(User).filter_by(id=msg.from_user.id).update(
                    {'tg_name': msg.from_user.username}
                )
            else:
                user = User(msg.from_user.id, msg.from_user.username)
                session.add(user)
            session.commit()


    @classmethod
    def set_can_be_supporte(cls, callback_query: types.CallbackQuery):
        with Session() as session:
            # setting that user has chosen some services and ready to ask for support now
            user_from_db = session.query(User).get(callback_query.from_user.id)
            if user_from_db:
                session.query(User).filter_by(id=callback_query.from_user.id).update(
                    {'can_be_supporte': True}
                )
                session.commit()

    @classmethod
    def can_be_supported(cls, msg: types.Message):
        """
        we need to check some conditions to let our bot support this user
        :param msg: message from chat
        :return: None
        """
        user_can_be_supported = [None, None]
        with Session() as session:
            user_from_db = session.query(User).get(msg.from_user.id)    # get current user from db
            support_delay_in_seconds = 0
            if user_from_db:
                if user_from_db.last_supported:
                    support_delay = datetime.datetime.now() - user_from_db.last_supported
                    support_delay_in_seconds = support_delay.seconds
                user_can_be_supported[0] =  True if not user_from_db.last_supported \
                                    or support_delay_in_seconds > SUPPORT_DELAY else False  # user can be supported if he hasn't been supported for last SUPPORT_DELAY seconds or has never been supported
                user_can_be_supported[1] = user_from_db.can_be_supporte     # second condition is user had chosen some services
                if all(user_can_be_supported):  # if he can be supported we set time of last support to this user
                    session.query(User).filter_by(id=msg.from_user.id).update(
                        {'last_supported': datetime.datetime.now()}
                    )
                    session.commit()
        return user_can_be_supported


    @classmethod
    def find_all(cls):
        # finds all user ids to send noticifications
        with Session() as session:
            users_list = session.query(User.id).all()
        return users_list
