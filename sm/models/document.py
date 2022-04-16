from sqlalchemy import Column, Integer, ForeignKey, Date, JSON
from sqlalchemy.sql import func
from .meta import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    date_created = Column(Date, default=func.current_date())
    date_changed = Column(Date, onupdate=func.current_date())
    user_id = Column(Integer, ForeignKey("users.id"))
    data = Column(JSON)
