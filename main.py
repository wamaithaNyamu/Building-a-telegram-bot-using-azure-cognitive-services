import os
import time

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


# https://stackoverflow.com/questions/50576426/microsoft-azure-cognitive-services-handwriting-detection-bounding-box-parameters
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


