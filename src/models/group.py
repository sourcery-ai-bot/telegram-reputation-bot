from sqlalchemy import Column, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Group(Base):

    __tablename__ = "group"

    group_id = Column(BigInteger, primary_key=True)
    last_message_id = Column(BigInteger, nullable=True)

    users = relationship("User", backref="groups", foreign_keys="User.group_id")

