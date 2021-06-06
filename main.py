import logging
import json
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# ===============CONFIG===============
with open("config.json", "r") as f:
    data = json.load(f)

CHATID = data["chatid"]
TOKEN = data["token"]

print(CHATID)
print(TOKEN)


# Enable logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
        )

logger = logging.getLogger(__name__)


# ===============FUNCTIONS===============
# Define a few command handlers. These usually take the two arguments update and
# context.

def votar_usuario(to_user_id: str, from_user_id: str) -> str:
    return ""


def vote(update: Update, context: CallbackContextpdate):
    msg = update.message

    if msg.text != "+" or msg.text != "-":
        return

    from_user_id = msg.from_user.id
    from_username = msg.from_user.username
    to_user_id = msg.reply_to_message.from_user.id
    to_username = msg.reply_to_message.from_user.username

    if msg.reply_to_message is None:
        pass
    elif not msg.reply_to_message.text:
        pass
    elif (msg.reply_to_message.text == "-" or msg.reply_to_message.text == "+"):
        msg.reply_text(text="No puedes votar votos")
    elif msg.reply_to_message.text.startswith("/"):
        msg.reply_text(text="No puedes votar comandos")
    elif msg.reply_to_message.text.startswith("/"):
        msg.reply_text(text="No puedes votar comandos")
    elif msg.reply_to_message.from_user.is_bot:
        msg.reply_text(text="No puedes votar a bots")
    elif from_user_id == to_user_id:
        msg.reply_text(text="No puedes votarte a ti mismo")
    else:
        voto_html = votar_usuario(to_user_id, from_user_id, msg.text)
        msg.reply_html(voto_html)


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
            fr'Hi {user.mention_markdown_v2()}\!',
            reply_markup=ForceReply(selective=True),
            )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)


# ===============MAIN===============

def main() -> None:
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
