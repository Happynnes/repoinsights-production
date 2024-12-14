from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    owner_id = Column(String)
    name = Column(String)
    deleted = Column(Boolean)
    forked_from = Column(Boolean, nullable=True)
