from sqlalchemy import Column, Integer, Text, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import event

from .meta import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    login = Column(String, index=True, unique=True)
    password = Column(String)
    position = Column(Text)
    date_last_document = Column(Date)
    boss_id = Column(Integer, ForeignKey("users.id"))
    staff = relationship("User")
    document = relationship("Document")


@event.listens_for(User.document, "append")
def receive_append(target, value, initiator):
    target.date_last_document = func.current_date()
