import os
from dotenv import load_dotenv
from flask import Flask
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CommandHandler
from main import GetTextRead, GetTextOcr
load_dotenv()


TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

app = Flask(__name__)


@app.route('/')
def extract_text_from_telegram(update, context):
    try:
        print("Uploading to telegram ...")
    except Exception as ex:
        update.message.reply_text("Upload an image with text")
        print(ex)


# set up the introductory statement for the bot when the /start command is invoked
def start(update, context):
    try:
        chat_id = update.effective_chat.id
        context.bot.send_message(chat_id=chat_id,
                                 text="Hello there, Wamaitha here. Thank you for registering for the event. \n"
                                      "This bot takes in a photo and applies the azure cognitive service to extract printed or handwritten text from images or pdfs. Have fun while at it! \n"
                                      "Connect with me  :\n"
                                      "Linkedin : https://www.linkedin.com/in/wamaithanyamu/\n"
                                      "Github : https://github.com/wamaithaNyamu \n"
                                      "Twitter : https://twitter.com/wamaithaNyamu \n")


    except Exception as ex:
        print(ex)


# run the start function when the user invokes the /start command
dispatcher.add_handler(CommandHandler("start", start))

dispatcher.add_handler(MessageHandler(Filters.all, extract_text_from_telegram))
updater.start_polling()


# print
if __name__ == '__main__':
    app.run(debug=True)
