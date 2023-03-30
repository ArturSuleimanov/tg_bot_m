from sqlalchemy import Column, Integer, String

from models.database import Base

from models.database import Session


class Question(Base):
    # Question table description

    __tablename__ = 'question'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    answer = Column(String, nullable=False)


    def __init__(self, title: str, answer: str) -> None:
        self.title = title
        self.answer = answer


    @classmethod
    def get_question_answer_by_id(cls, id: int):
        # gives us answer to question we need
        with Session() as session:
            return session.query(Question).get(id).answer


    @classmethod
    def get_questions_list(cls):
        # gives us every question from db
        with Session() as session:
            return session.query(Question).all()
