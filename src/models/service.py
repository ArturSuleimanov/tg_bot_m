from sqlalchemy import Column, Integer, String
from models.database import Base
from models.database import Session


class Service(Base):
    # service table description

    __tablename__ = 'service'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    short_description = Column(String, nullable=False)
    more_detailed_description = Column(String, nullable=False)
    price = Column(Integer, nullable=False, default=0)


    def __init__(self,
                 title: str,
                 short_description: str,
                 more_detailed_description: str,
                 price: int) -> None:
        self.title = title
        self.short_description = short_description
        self.more_detailed_description = more_detailed_description
        self.price = price


    @classmethod
    def get_by_id(cls, id: int):
        with Session() as session:
            return session.query(Service).get(id)


    @classmethod
    def get_services_list(cls):
        # gives us every service from db
        with Session() as session:
            services_list = session.query(Service.id, Service.title).all()
        return services_list


    def __hash__(self):
        return hash(self.id)


    def __eq__(self, other):
        if isinstance(other, Service):
            return self.id == other.id
        return False
