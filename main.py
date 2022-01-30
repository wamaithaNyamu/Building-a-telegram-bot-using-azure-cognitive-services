import os
import time
from PIL import Image, ImageDraw
from matplotlib import pyplot as plt

# Import namespaces
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials

from dotenv import load_dotenv

# Get Configuration Settings
load_dotenv()
cog_endpoint = os.getenv('COG_SERVICE_ENDPOINT')
cog_key = os.getenv('COG_SERVICE_KEY')

# Authenticate Computer Vision client
credential = CognitiveServicesCredentials(cog_key)
cv_client = ComputerVisionClient(cog_endpoint, credential)



def GetTextOcr(file_path):
    """
    Takes in a file and does OCR on the document and returns a string
    of the text extracted during OCR.
    :param file_path:
    :return: string
    """
    try:
        print("This function invokes the OCR API on", file_path)
    except Exception as ex:
        print(ex)


def GetTextRead(file_path):
    """
      Takes in a file and extracts handwritten or printed text
       on the document and returns a string of the text extracted during OCR.
      :param file_path:
      :return: string
    """
    try:
       print("This function invokes the READ API on", file_path)
    except Exception as ex:
        print(ex)


def ask_user_for_input():

    """
    Asks the user for input from the command line

    """
    try:

        # Menu for text reading functions
        print('1: Use OCR API\n2: Use Read API\n3: Read handwriting\nAny other key to quit')
        command = input('Enter a number:')
        if command == '1':
            image_file = os.path.join('images', 'chinua.png')
            GetTextOcr(image_file)
        elif command == '2':
            image_file = os.path.join('images', 'story.pdf')
            GetTextRead(image_file)
        elif command == '3':
            image_file = os.path.join('images', 'wams.png')
            GetTextRead(image_file)


    except Exception as ex:
        print(ex)


ask_user_for_input()
