from datetime import datetime, timedelta

from sqlalchemy import create_engine, func, null
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import session
from telegram import Bot, Update

from config import DB, TOKEN
from models import User, Group, UserVotes

Base = declarative_base()


def mention(user: User) -> str:
    return f'<a href="tg://user?id={user.user_id}">{user.name}</a>'


# Check / Create
def check_group(group_id: int, session_func: session.Session) -> Group:
    group = session_func.query(Group).filter(Group.group_id == group_id).first()

    if group is not None:
        return group

    group = Group(group_id=group_id)
    session_func.add(group)
    session_func.commit()

    return group


def check_user(user: User, group_id: int, session_func: session.Session) -> User:

    check_group(group_id, session_func)

    user_result = (
        session_func.query(User)
        .filter(User.user_id == user.id)
        .filter(User.group_id == group_id)
        .first()
    )

    if user == user_result:
        return user

    user.group_id = group_id  # type: ignore


    session_func.add(user)
    session_func.commit()

    return user


def vote_user(
    from_user: User,
    to_user: User,
    group_id: int,
    vote: str,
    message_id: int,
    session_func: session.Session,
) -> str:
    vote_input = -1
    from_user = check_user(from_user, group_id, session_func)

    to_user = check_user(to_user, group_id, session_func)

    if (
        session_func.query(UserVotes)
        .filter(UserVotes.message_id == message_id)
        .filter(UserVotes.from_user_id == from_user.id)
        .filter(UserVotes.group_id == group_id)
        .first()
    ):
        return ""

    if vote == "+":
        to_user.reputation = to_user.reputation + 1
        vote_input = 1
    else:
        to_user.reputation = to_user.reputation - 1

    uservote = UserVotes(
        from_user_id=from_user.user_id,
        to_user_id=to_user.user_id,
        vote=vote_input,
        group_id=group_id,
        message_id=message_id,
    )

    session_func.add(to_user)
    session_func.add(uservote)

    session_func.commit()

    return str(uservote)


def show_voted_rep(
    html_reply: str,
    group_id: int,
    session_func: session.Session,
    update: Update,
) -> None:
    bot = Bot(TOKEN)
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
def top_leaderboard(
    session_func: session.Session,
    groupid: int,
    weeks: int,
    top_show: int,
    update: Update,
) -> None:
    # CHECK: hybrid_propery

    leaderboard_str = ""
    weeks_ago = datetime.now() - timedelta(weeks=weeks)

    leaderboard = (
        session_func.query(UserVotes.to_user_id, func.sum(UserVotes.vote))
        .filter(UserVotes.group_id == groupid)
        .filter(UserVotes.voted_at > weeks_ago)
        .group_by(UserVotes.to_user_id)
        .order_by(func.sum(UserVotes.vote).desc(), UserVotes.to_user_id)
        .limit(top_show)
        .all()
    )

    for index, user in enumerate(leaderboard):
        try:
            user_o = session_func.query(User).filter(User.user_id == user[0]).first()
            rep_leaderboard = user[1]
            leaderboard_str += f"{index + 1}º - {mention(user_o)} - {rep_leaderboard}\n"
        except Exception as e:
            print(e)
            continue

    if leaderboard_str:
        update.message.reply_html(leaderboard_str)
    else:
        update.message.reply_html("No hay usuarios en la lista")


if __name__ == "__main__":
    engine = create_engine(DB)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
