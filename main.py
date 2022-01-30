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

    """
    try:
        print("This function invokes the OCR API on", file_path)
        # Use OCR API to read text in image
        with open(file_path, mode="rb") as image_data:
            ocr_results = cv_client.recognize_printed_text_in_stream(image_data)

        # Prepare image for drawing
        fig = plt.figure(figsize=(7, 7))
        img = Image.open(file_path)
        draw = ImageDraw.Draw(img)

        # All the words extracted will be stored as a list
        results = []
        print(ocr_results)
        # Process the text line by line
        for region in ocr_results.regions:
            for line in region.lines:

                # Show the position of the line of text
                l, t, w, h = list(map(int, line.bounding_box.split(',')))
                draw.rectangle(((l, t), (l + w, t + h)), outline='magenta', width=5)

                # Read the words in the line of text
                line_text = ''
                for word in line.words:
                    line_text += word.text + ' '
                print(line_text.rstrip())
                results.append(line_text.rstrip())

        # Save the image with the text locations highlighted if the image was ocrd
        if len(results) > 0:
            plt.axis('off')
            plt.imshow(img)
            # create output folder if doesnt exist
            if not os.path.exists('ocr-results'):
                os.makedirs('ocr-results')
            file_path = file_path.rsplit('\\', 1)[-1].rsplit('.', 1)[0]
            outputfile = f'ocr-results\\{file_path}-ocr_results.jpg'
            fig.savefig(outputfile)
            print('Results saved in', outputfile)
            # if there was no ocr decoded the results list will be empty
        if len(results) == 0:
            print(f'{file_path} IMAGE WAS NOT OCRD')


    except Exception as ex:
        print(ex)


def GetTextRead(file_path):
    """
      Takes in a file and extracts handwritten or printed text
       on the document and returns a string of the text extracted during OCR.
      :param file_path:
    """
    try:
        print("This function invokes the READ API on", file_path)
        results = []
        # Use Read API to read text in image
        with open(file_path, mode="rb") as image_data:
            read_op = cv_client.read_in_stream(image_data, raw=True)

        # Get the async operation ID so we can check for the results
        operation_location = read_op.headers["Operation-Location"]
        operation_id = operation_location.split("/")[-1]

        # Wait for the asynchronous operation to complete
        while True:
            read_results = cv_client.get_read_result(operation_id)
            if read_results.status not in [OperationStatusCodes.running, OperationStatusCodes.not_started]:
                break
            time.sleep(1)

        # If the operation was successfuly, process the text line by line
        if read_results.status == OperationStatusCodes.succeeded:
            for page in read_results.analyze_result.read_results:
                for line in page.lines:
                    print(line.text)
                    results.append(line.text)
        print('Reading text in {}\n'.format(file_path))

        return results
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
            file_path = os.path.join('images', 'abc.png')
            GetTextOcr(file_path)
        elif command == '2':
            file_path = os.path.join('images', 'story.pdf')
            GetTextRead(file_path)
        elif command == '3':
            file_path = os.path.join('images', 'wams.png')
            GetTextRead(file_path)


    except Exception as ex:
        print(ex)


ask_user_for_input()
