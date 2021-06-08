"""
def nuevo_usuario(session, userid, username):
    if session.query(User).get(userid):
        return
    user = User(id=userid, username=username)
    session.add(user)
    session.commit()

def dar_reputacion(
        session,
        to_userid, to_username,
        from_userid, from_userid,
        vote, groupid):

    if session.query(User).get(to_userid):
        pass
"""































from sqlalchemy import Column, String, Integer, BigInteger, ForeignKey, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

engine = create_engine("mysql+pymysql://admin:root@localhost/telegrambot")
Base = declarative_base()
Session = sessionmaker(engine)
session = Session()

class User(Base):

    __tablename__ = "user"

    id = Column("id", BigInteger, primary_key=True)
    username = Column("username", String(32), nullable=True, unique=True)
    reputation = Column("reputation", Integer, default=0)

    voted = relationship("UserVotes", backref = "fromuser", foreign_keys = "UserVotes.fromuser_id")
    votes = relationship("UserVotes", backref = "touser", foreign_keys = "UserVotes.touser_id")

    def __str__(self):
        return f"{self.id} - {self.username}"

class UserVotes(Base):

    __tablename__ = "uservotes"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    groupid = Column("groupid", BigInteger)
    fromuser_id = Column("from_userid", ForeignKey("user.id"))
    touser_id = Column("to_userid", ForeignKey("user.id"))
    voted_at = Column("voted_at", DateTime, default=datetime.now())


    def __str__(self):
        return f"{self.fromuser} votó a {self.touser}"


def check_user(id: int, username: str) -> None:
    if (session.query(User).filter(User.id == id).first() is not None):
        pass
    else:
        user = User(id=id, username=username)
        session.add(user)
        session.commit()


if __name__ == "__main__":
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    check_user(1, "A")
    check_user(2, "B")
    check_user(3, "C")

    vote  = UserVotes(groupid=1, fromuser_id=1, touser_id=2)
    vote2 = UserVotes(groupid=1, fromuser_id=1, touser_id=2)
    vote3 = UserVotes(groupid=1, fromuser_id=1, touser_id=2)
    vote4 = UserVotes(groupid=1, fromuser_id=3, touser_id=1)
    session.add(vote)
    session.add(vote2)
    session.add(vote3)
    session.add(vote4)
    session.commit()
