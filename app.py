import os
from dotenv import load_dotenv
from flask import Flask
import requests
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CommandHandler

# from our main.py
from main import GetTextRead

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

app = Flask(__name__)


def file_handler(update):
    try:
        print(update.message)
        file_id = ''

        if len(update.message.photo) == 0 and update.message.document.file_id:
            print("WE HAVE A DOCUMENT", update.message.document.file_id)
            file_id = update.message.document.file_id

        elif len(update.message.photo) > 0:
            print("WE HAVE AN IMAGE", update.message.photo[-1].file_id)
            file_id = update.message.photo[-1].file_id

        return file_id

    except Exception as e:
        print("Handler exception", e)


@app.route('/')
def extract_text_from_telegram(update, context):
    """

    :param update: checks for updates from telegram
    :param context:
    :return:
    """
    try:

        print("Uploading to telegram ...", )
        file_id = file_handler(update)

        print("FILE ID", file_id)

        if file_id:
            update.message.reply_text("Processing file...")
            file_path = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={file_id}'
            img = requests.get(file_path).json()
            img = img['result']['file_path']

            file_image = f'https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{img}'
            response = requests.get(file_image)

            img_name = img.rsplit('/', 1)[-1]

            file = open(f'{img_name}', "wb")
            file.write(response.content)
            file.close()
            user_image_text_results = GetTextRead(img_name)
            if len(user_image_text_results) > 0:
                results = ' '.join(str(e) for e in user_image_text_results)
                print(results)
                update.message.reply_text("Thank you for your patience. This is what I extracted:")
                update.message.reply_text(results)
            else:
                update.message.reply_text(
                    "Unfortunately, this image or document does not contain any printed or handwritten text. ")

        else:
            update.message.reply_text("Upload an image or document with text")

        if os.path.exists(img_name):
            os.remove(img_name)
            print(img_name, ' deleted!')
        else:
            print(f"The file {img_name} does not exist")

    except Exception as ex:
        update.message.reply_text(f'Something went wrong contact admin')
        print(ex)


# set up the introductory statement for the bot when the /start command is invoked
def start(update, context):
    """
    /start command on telegram
    :param update:
    :param context:
    :return:
    """
    try:
        chat_id = update.effective_chat.id
        context.bot.send_message(chat_id=chat_id,
                                 text="Demo time!!!")


    except Exception as ex:
        print(ex)


# run the start function when the user invokes the /start command
dispatcher.add_handler(CommandHandler("start", start))

dispatcher.add_handler(MessageHandler(Filters.all, extract_text_from_telegram))
# updater.start_polling()

# add the webhook code
updater.start_webhook(listen="0.0.0.0",
                      port=int(os.environ.get('PORT', 8080)),
                      url_path=TELEGRAM_TOKEN,
                      webhook_url=os.getenv('BOT_URL') + TELEGRAM_TOKEN
                      )

if __name__ == '__main__':
    app.run(debug=True)
