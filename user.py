from datetime import datetime, timedelta

from sqlalchemy import Column, String, Integer, BigInteger,Boolean, DateTime, create_engine, null, func
from sqlalchemy.schema import ForeignKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, session

from telegram import Bot, Update

engine = create_engine("mysql+pymysql://admin:root@localhost/telegrambot")
Base = declarative_base()

class Group(Base):

    __tablename__ = "group"

    group_id = Column(BigInteger, primary_key=True)
    last_message_id = Column(BigInteger, nullable=True)

    users = relationship("User", backref = "groups",
                         foreign_keys = "User.group_id")

class User(Base):

    __tablename__ = "user"

    user_id = Column(BigInteger, primary_key=True)
    group_id = Column(BigInteger, primary_key=True)

    username = Column(String(32), nullable=True)
    name = Column(String(100), nullable=False)

    reputation = Column(Integer, default=0, nullable=False)

    voted = relationship("UserVotes", backref = "fromuser",
                         foreign_keys = "UserVotes.from_user_id",
                         primaryjoin="and_(User.user_id==UserVotes.from_user_id, "
                                     "User.group_id==UserVotes.group_id)")
    votes = relationship("UserVotes", backref = "touser",
                         foreign_keys = "UserVotes.to_user_id",
                         primaryjoin="and_(User.user_id==UserVotes.to_user_id, "
                                     "User.group_id==UserVotes.group_id)")

    __table_args__ = (
        ForeignKeyConstraint(
            ['group_id'],
            ['group.group_id'],
            name="fk_group_id"
        ),)

    def __str__(self):
        return f'<a href="tg://user?id={self.user_id}">{self.name}</a> [{self.reputation}]'

class UserVotes(Base):

    __tablename__ = "uservotes"

    id = Column(Integer, primary_key=True, autoincrement=True)

    group_id = Column(BigInteger, nullable=False)

    from_user_id = Column(BigInteger, nullable=False)
    to_user_id = Column(BigInteger, nullable=False)
    message_id = Column(BigInteger, nullable=False)

    vote = Column(Boolean)

    voted_at = Column(DateTime, default=datetime.now())
    __table_args__ = (
        ForeignKeyConstraint(
            ['from_user_id', 'group_id'],
            ['user.user_id', 'user.group_id'],
            name="fk_from_group_id"
        ),
        ForeignKeyConstraint(
            ['to_user_id', 'group_id'],
            ['user.user_id', 'user.group_id'],
           name="fk_to_group_id"
        ),
    )

    def __str__(self):
        return f"{self.fromuser} votó a {self.touser} con {self.vote}1"


# Check / Create
def check_group(group_id: int, session: session.Session) -> Group:
    group = session.query(Group).filter(Group.group_id == group_id).first()

    if group is not None:
        return group

    group = Group(group_id = group_id)
    session.add(group)
    session.commit()

    return group

def check_user(user_id: int, username: str, name: str, group_id: int, session: session.Session) -> User:

    check_group(group_id, session)

    user = session.query(User)\
                  .filter(User.user_id == user_id)\
                  .filter(User.group_id == group_id).first()

    if (user is not None):
        return user

    user = User(user_id=user_id, username=username, name=name, group_id=group_id)
    session.add(user)
    session.commit()
    return user

def get_last_message_id(group_id: int, session: session.Session) -> int:
    group = check_group(group_id, session)
    if group.last_message_id == None:
        return 0
    return group.last_message_id


def vote_user(from_user_id: int, from_username: str, from_user_name: str,
              to_user_id: int, to_username: str, to_user_name: str,
              group_id: int, vote: str, message_id: int, session: session.Session ) -> str:
    from_user = check_user(from_user_id, from_username, from_user_name, group_id, session)

    to_user = check_user(to_user_id, to_username, to_user_name, group_id, session)

    if session.query(UserVotes)\
              .filter(UserVotes.message_id == message_id)\
              .filter(UserVotes.from_user_id == from_user_id)\
              .filter(UserVotes.group_id == group_id).first():
        return ""

    if vote == "+":
        to_user.reputation = to_user.reputation + 1
    else:
        to_user.reputation = to_user.reputation - 1


    uservote = UserVotes(from_user_id=from_user.user_id, to_user_id=to_user.user_id,
                         vote=vote, group_id=group_id, message_id=message_id)
    session.add(to_user)
    session.add(uservote)

    session.commit()

    return str(uservote)


def show_voted_rep(html_reply: str, group_id: int, session: session.Session, bot: Bot, update: Update) -> None:
    group = check_group(group_id, session)

    if group.last_message_id is not None:
        print(group.last_message_id)
        print("#2")
        bot.delete_message(chat_id=group_id, message_id=group.last_message_id)
        group.last_message_id = null()
        session.add(group)
        session.commit()

    group.last_message_id = update.message.reply_html(html_reply).message_id
    session.add(group)
    session.commit()



# Leaderboards
def top_leaderboard(session: session.Session, groupid: int, weeks=999) -> str:
    # CHECK: hybrid_propery

    session.execute(f'''
SELECT
	to_user_id, (count(vote) -
		(SELECT count(*) from uservotes as ue
		 	where ue.vote = "-" AND ue.to_user_id = uservotes.to_user_id
		 					   AAND (date_add(ue.voted_at, INTERVAL {weeks} WEEK) > NOW()))
	 )
FROM uservotes
WHERE vote = "+" AND (date_add(uservotes.voted_at, INTERVAL {weeks} WEEK) > NOW())
GROUP BY to_user_id
ORDER BY 2;
            ''')
    return ""


if __name__ == "__main__":

    engine = create_engine("mysql+pymysql://admin:root@localhost/telegrambot")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    #check_user(1, "A", "Aa", 3)
    #check_user(2, "B", "Ba", 4)

    """vote  = UserVotes(from_user_id=1, to_user_id=2, vote="+", group_id=2)
    vote2 = UserVotes(from_user_id=1, to_user_id=2, vote="-")
    vote3 = UserVotes(from_user_id=1, to_user_id=2, vote="-")
    vote4 = UserVotes(from_user_id=3, to_user_id=1, vote="+")
    session.add(vote)
    session.add(vote2)
    session.add(vote3)
    session.add(vote4)"""
    #session.commit()
