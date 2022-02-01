import os
import pathlib

from dotenv import load_dotenv
from flask import Flask
import requests
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CommandHandler
from main import GetTextRead

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

app = Flask(__name__)


@app.route('/')
def extract_text_from_telegram(update, context):
    """

    :param update: checks for updates from telegram
    :param context:
    :return:
    """
    try:
        print("Uploading to telegram ...")
        file_id = update.message.photo[-1].file_id
        file_name = ''

        if file_id:
            update.message.reply_text("Processing image...")
            file_path = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={file_id}'
            img = requests.get(file_path).json()
            img = img['result']['file_path']
            # img path: photos/file_35.jpg
            print("img path:", img)
            file_image = f'https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{img}'
            response = requests.get(file_image)
            # split_img path: file_35.jpg
            split_img = img.rsplit('/', 1)[-1]
            print("split_img path:", split_img)

            # File Extension:  .jpg
            file_extension = pathlib.Path(split_img).suffix
            print("File Extension: ", file_extension)
            # file_35.jpg-AgACAgQAAxkBAAIBS2H5FN20IK2ArluFlw_E_MiY2bw.jpg
            file_name = f'{split_img}-{file_id}.{file_extension}'

            file = open(f'{file_name}', "wb")
            file.write(response.content)
            file.close()

            user_image_text_results = GetTextRead(file_name)
            print("results:", user_image_text_results)
            if len(user_image_text_results) > 0:
                results = ' '.join(str(e) for e in user_image_text_results)
                print(results)
                update.message.reply_text("Thank you for your patience. This is what I extracted:")
                update.message.reply_text(results)
            else:
                update.message.reply_text(
                    "Unfortunately, this image does not contain any printed or handwritten text. ")

        else:
            update.message.reply_text("Upload an image with text")

        if os.path.exists(file_name):
            os.remove(file_name)
            print(file_name, ' deleted!')
        else:
            print(f"The file {file_name} does not exist")
    except Exception as ex:
        update.message.reply_text("Upload an image with text")
        print(ex)

    except Exception as ex:
        update.message.reply_text("Upload an image with text")
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
                                 text="Hello there, Wamaitha here. Thank you for registering for the event. \n"
                                      "This bot takes in a photo and applies the azure cognitive service to extract "
                                      "printed or handwritten text from images or pdfs. Have fun while at it! \n "
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
