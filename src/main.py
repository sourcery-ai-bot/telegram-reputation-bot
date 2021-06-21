import logging
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from telegram import Update
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler, Updater)

from config import DB, TOKEN
from funcs import show_voted_rep, top_leaderboard, vote_user
from models import User

# ===============Logging===============
logging.basicConfig(
    format=
    '%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO,
    filename="app.log")

logger = logging.getLogger(__name__)

# ===============FUNCTIONS===============
engine = create_engine(DB)
Session = sessionmaker(engine)


@contextmanager
def session_scope():
    """Contextmanager for sqlalchemy sessions"""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        logger.exception("SQL problem")
        session.rollback()
    finally:
        session.close()


def vote(
        update: Update,
        _unused: CallbackContext  # type: ignore
):
    msg = update.message

    if msg is None:
        return
    if msg.text is None:
        return
    if msg.text not in ("+", "-"):
        return

    group_id = msg.chat.id

    if msg.reply_to_message is None:
        pass
    elif msg.reply_to_message.from_user.is_bot:
        msg.reply_text(text="No puedes votar a bots")
    elif msg.from_user.id == msg.reply_to_message.from_user.id:
        msg.reply_text(text="No puedes votarte a ti mismo")
    else:
        from_user = User(user_id=msg.from_user.id,
                         username=msg.from_user.name,
                         name="",
                         group_id=group_id)
        to_user = User(user_id=msg.reply_to_message.from_user.id,
                       username=msg.reply_to_message.from_user.name,
                       name="",
                       group_id=group_id)

        with session_scope() as session:
            html_reply = vote_user(
                from_user,
                to_user,
                group_id,
                msg.text,
                msg.reply_to_message.message_id,
                session,
            )
            if html_reply:
                show_voted_rep(html_reply, group_id, session, update)


def top_rep(update: Update, context: CallbackContext) -> None:
    try:
        limit = int(context.args[0])
    except ValueError:
        update.message.reply_html(
            "Tienes que poner un número con el límite de "
            "Usuarios a mostrar, o no poner nada "
            "para dejar 10 por defecto")
        return
    except IndexError:
        limit = 10
    with session_scope() as session:
        top_leaderboard(session, update.message.chat.id, 9999, limit, update)


def top_rep_weekly(update: Update, context: CallbackContext) -> None:
    try:
        time_limit = int(context.args[0])
    except ValueError:
        update.message.reply_html(
            "Tienes que poner un número con las semanas a mostrar, por defecto es 1"
        )
        return
    except IndexError:
        time_limit = 1
    with session_scope() as session:
        top_leaderboard(session, update.message.chat.id, time_limit, 20,
                        update)


def config_rep(update: Update, _unused: CallbackContext) -> None:
    pass


def main() -> None:
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    # Commands
    dispatcher.add_handler(CommandHandler("toprep", top_rep))
    dispatcher.add_handler(CommandHandler("weeklyrep", top_rep_weekly))
    dispatcher.add_handler(CommandHandler("configrep", config_rep))

    dispatcher.add_handler(MessageHandler(Filters.text, vote))

    # Start the bot
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
