from datetime import datetime, timedelta

from sqlalchemy import (BigInteger, Column, DateTime, Integer, SmallInteger,
                        String, create_engine, func, null)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, session
from sqlalchemy.schema import ForeignKeyConstraint
from telegram import Bot, Update

from config import DB

Base = declarative_base()


class Group(Base):

    __tablename__ = "group"

    group_id = Column(BigInteger, primary_key=True)
    last_message_id = Column(BigInteger, nullable=True)

    users = relationship("User",
                         backref="groups",
                         foreign_keys="User.group_id")


class User(Base):

    __tablename__ = "user"

    user_id = Column(BigInteger, primary_key=True)
    group_id = Column(BigInteger, primary_key=True)

    username = Column(String(32), nullable=True)
    name = Column(String(100), nullable=False)

    reputation = Column(Integer, default=0, nullable=False)

    voted = relationship(
        "UserVotes",
        backref="fromuser",
        foreign_keys="UserVotes.from_user_id",
        primaryjoin="and_(User.user_id==UserVotes.from_user_id, "
        "User.group_id==UserVotes.group_id)")
    votes = relationship(
        "UserVotes",
        backref="touser",
        foreign_keys="UserVotes.to_user_id",
        primaryjoin="and_(User.user_id==UserVotes.to_user_id, "
        "User.group_id==UserVotes.group_id)")

    __table_args__ = (ForeignKeyConstraint(['group_id'], ['group.group_id'],
                                           name="fk_group_id"), )

    def mention(self):
        return f'<a href="tg://user?id={self.user_id}">{self.name}</a>'

    def __str__(self):
        return f'<a href="tg://user?id={self.user_id}">'\
               '{self.name}</a> [{self.reputation}]'


class UserVotes(Base):

    __tablename__ = "uservotes"

    id = Column(Integer, primary_key=True, autoincrement=True)

    group_id = Column(BigInteger, nullable=False)

    from_user_id = Column(BigInteger, nullable=False)
    to_user_id = Column(BigInteger, nullable=False)
    message_id = Column(BigInteger, nullable=False)

    vote = Column(SmallInteger)

    voted_at = Column(DateTime, default=datetime.now())
    __table_args__ = (
        ForeignKeyConstraint(['from_user_id', 'group_id'],
                             ['user.user_id', 'user.group_id'],
                             name="fk_from_group_id"),
        ForeignKeyConstraint(['to_user_id', 'group_id'],
                             ['user.user_id', 'user.group_id'],
                             name="fk_to_group_id"),
    )

    def __str__(self):
        if self.vote == 1:
            return f"{self.fromuser} votó a {self.touser} con +1"

        return f"{self.fromuser} votó a {self.touser} con -1"


# Check / Create
def check_group(group_id: int, session_func: session.Session) -> Group:
    group = session_func.query(Group).filter(
        Group.group_id == group_id).first()

    if group is not None:
        return group

    group = Group(group_id=group_id)
    session_func.add(group)
    session_func.commit()

    return group


def check_user(user_id: int, username: str, name: str, group_id: int,
               session_func: session.Session) -> User:

    check_group(group_id, session_func)

    user = session_func.query(User)\
        .filter(User.user_id == user_id)\
        .filter(User.group_id == group_id).first()

    if user is not None:
        return user

    user = User(user_id=user_id,
                username=username,
                name=name,
                group_id=group_id)

    session_func.add(user)
    session_func.commit()
    return user


def vote_user(from_user_id: int, from_username: str, from_user_name: str,
              to_user_id: int, to_username: str, to_user_name: str,
              group_id: int, vote: str, message_id: int,
              session_func: session.Session) -> str:
    vote_input = -1
    from_user = check_user(from_user_id, from_username, from_user_name,
                           group_id, session_func)

    to_user = check_user(to_user_id, to_username, to_user_name, group_id,
                         session_func)

    if session_func.query(UserVotes)\
        .filter(UserVotes.message_id == message_id)\
        .filter(UserVotes.from_user_id == from_user_id)\
            .filter(UserVotes.group_id == group_id).first():
        return ""

    if vote == "+":
        to_user.reputation = to_user.reputation + 1
        vote_input = 1
    else:
        to_user.reputation = to_user.reputation - 1

    uservote = UserVotes(from_user_id=from_user.user_id,
                         to_user_id=to_user.user_id,
                         vote=vote_input,
                         group_id=group_id,
                         message_id=message_id)

    session_func.add(to_user)
    session_func.add(uservote)

    session_func.commit()

    return str(uservote)


def show_voted_rep(html_reply: str, group_id: int,
                   session_func: session.Session, bot: Bot,
                   update: Update) -> None:
    group = check_group(group_id, session_func)

    if group.last_message_id is not None:
        bot.delete_message(chat_id=group_id, message_id=group.last_message_id)
        group.last_message_id = null()
        session_func.add(group)
        session_func.commit()

    group.last_message_id = update.message.reply_html(html_reply).message_id
    session_func.add(group)
    session_func.commit()


# Leaderboards
def top_leaderboard(session_func: session.Session, groupid: int, weeks: int,
                    top_show: int, update: Update) -> None:
    # CHECK: hybrid_propery

    leaderboard_str = ""
    weeks_ago = datetime.now() - timedelta(weeks=weeks)

    leaderboard = session_func.query(UserVotes.to_user_id, func.sum(UserVotes.vote))\
        .filter(UserVotes.group_id == groupid)\
        .filter(UserVotes.voted_at > weeks_ago)\
        .group_by(UserVotes.to_user_id)\
        .order_by(func.sum(UserVotes.vote).desc())\
        .limit(top_show).all()

    for index, user in enumerate(leaderboard):
        try:
            rep_leaderboard = user[1]
            leaderboard_str += f"{index + 1}º - {user.mention()} - {rep_leaderboard}\n"
        except Exception:
            continue

    if leaderboard_str:
        update.message.reply_html(leaderboard_str)
    else:
        update.message.reply_html("No hay usuarios en la lista")


if __name__ == "__main__":
    engine = create_engine(DB)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
