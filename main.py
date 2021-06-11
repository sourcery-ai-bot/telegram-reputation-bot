import logging
import sys
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from telegram import Bot, Update
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler, Updater)

from config import DB, TOKEN
from user import show_voted_rep, top_leaderboard, vote_user

# ===============CONFIG===============

bot = Bot(TOKEN)


# Enable logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
        )

logger = logging.getLogger(__name__)


# ===============FUNCTIONS===============
# Define a few command handlers. These usually take the two arguments update and
# context.

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
        session.rollback()
        raise
    finally:
        session.close()


def vote(update: Update, _unused: CallbackContext):
    msg = update.message

    if msg is None:
        return
    if msg.text is None:
        return
    if not msg in ("+", "-"):
        return

    group_id = msg.chat.id

    from_user_id = msg.from_user.id
    from_username = msg.from_user.username
    from_user_name = msg.from_user.name

    to_user_id = msg.reply_to_message.from_user.id
    to_username = msg.reply_to_message.from_user.username
    to_user_name = msg.reply_to_message.from_user.name

    if msg.reply_to_message is None:
        pass
    elif msg.reply_to_message.from_user.is_bot:
        msg.reply_text(text="No puedes votar a bots")
    elif from_user_id == to_user_id:
        msg.reply_text(text="No puedes votarte a ti mismo")
    else:
        with session_scope() as session:
            html_reply = vote_user(from_user_id, from_username, from_user_name,
                                   to_user_id, to_username, to_user_name,
                                   group_id, msg.text,
                                   msg.reply_to_message.message_id, session)
            if html_reply:
                show_voted_rep(html_reply, group_id, session, bot, update)


def top_rep(update: Update, context: CallbackContext):
    try:
        limit = int(context.args[0])
    except ValueError:
        update.message.reply_html("Tienes que poner un número con el límite de "
                                  "Usuarios a mostrar, o no poner nada "
                                  "para dejar 10 por defecto")
        return
    except IndexError:
        limit = 10
    with session_scope() as session:
        top_leaderboard(session, update.message.chat.id, 9999, limit, update)


def top_rep_weekly(update: Update, context: CallbackContext):
    try:
        time_limit = int(context.args[0])
    except ValueError:
        update.message.reply_html("Tienes que poner un número con "
                                  "las semanas a mostrar, por defecto es 1")
        return
    except IndexError:
        time_limit = 1
    with session_scope() as session:
        top_leaderboard(session, update.message.chat.id,
                        time_limit, 20, update)


# ===============MAIN===============


def main() -> None:
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("toprep", top_rep))
    dispatcher.add_handler(CommandHandler("repweekly", top_rep_weekly))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text, vote))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
