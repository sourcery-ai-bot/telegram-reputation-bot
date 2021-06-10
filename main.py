import logging
import json

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from telegram import Update, ForceReply, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from user import vote_user, show_voted_rep

# ===============CONFIG===============
with open("config.json", "r") as f:
    data = json.load(f)

TOKEN = data["token"]
bot = Bot(TOKEN)


# Enable logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
        )

logger = logging.getLogger(__name__)


# ===============FUNCTIONS===============
# Define a few command handlers. These usually take the two arguments update and
# context.

engine = create_engine("mysql+pymysql://admin:root@localhost/telegrambot")
Session = sessionmaker(engine)

@contextmanager
def session_scope():
    """Contextmanager for sqlalchemy sessions"""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def vote(update: Update, context: CallbackContext):
    msg = update.message
    print(msg.reply_to_message)

    if msg is None:
        return
    if msg.text is None:
        return
    if msg.text != "+" and msg.text != "-":
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
                      group_id, msg.text, msg.reply_to_message.message_id, session)
            if html_reply:
                show_voted_rep(html_reply, group_id, session, bot, update)





# ===============MAIN===============

def main() -> None:
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text, vote))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
