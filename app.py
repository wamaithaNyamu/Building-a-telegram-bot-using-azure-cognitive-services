import requests
import os
from dotenv import load_dotenv
from flask import Flask

# telegram
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CommandHandler

# OCR API function from main.py
from main import GetTextRead
# writing to pdf from write_to_pdf.py
from write_to_pdf import add_to_pdf

load_dotenv()

# server settings
DEBUG_MODE = True
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
        img_name = ''
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
                update.message.reply_text("Saving results to pdf ...")

                #     add to pdf

                chat_id = update.effective_chat.id
                pdf_name = f'{chat_id}.pdf'

                pdf_name = add_to_pdf(pdf_name, user_image_text_results)
                update.message.reply_text("Added to pdf")

                document = open(pdf_name, 'rb')
                context.bot.send_document(chat_id, document)


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
                                 text="Start command sequence began..")

        pdf_name = f'{chat_id}.pdf'

        if os.path.exists(pdf_name):
            os.remove(pdf_name)
            print(pdf_name, ' deleted!')

            context.bot.send_message(chat_id=chat_id,
                                     text="Existing pdf deleted.")

        else:

            context.bot.send_message(chat_id=chat_id,
                                     text="You do not have any PDF's on file")

            print(f"The file {pdf_name} does not exist")


    except Exception as ex:
        print(ex)


# run the start function when the user invokes the /start command
dispatcher.add_handler(CommandHandler("start", start))

dispatcher.add_handler(MessageHandler(Filters.all, extract_text_from_telegram))
updater.start_polling()


# add the webhook code
updater.start_webhook(listen="0.0.0.0",
                      port=int(os.getenv('PORT')),
                      url_path=TELEGRAM_TOKEN,
                      webhook_url=os.getenv('BOT_URL') + TELEGRAM_TOKEN
                      )

