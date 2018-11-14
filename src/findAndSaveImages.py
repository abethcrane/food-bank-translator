import  urllib.parse, uuid, json, requests
from openpyxl import Workbook, load_workbook
from openpyxl.drawing.image import Image
from PIL import Image
from io import BytesIO

search_url = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"
maxTries = 5

class ImageDownloader():

    subscriptionKey = open("../subscriptionKeys/imageSubscriptionKey.txt").read()

    def main(self, spreadsheetLocation):   
        if spreadsheetLocation == "":
            spreadsheetLocation = "../translatedWords.xlsx"

        print("I'll print each word when I finish downloading a thumbnail for it")

        # Initialize the spreadsheet
        workbook = load_workbook(filename = spreadsheetLocation)
        worksheet = workbook["translations"]

        for rowNum in range(2, worksheet.max_row + 1):
            englishWordCell = "A{}".format(rowNum)
            englishWord = worksheet[englishWordCell].value

            if englishWord is None or englishWord is "":
                continue

            (img, _) = self.getNextImage(englishWord, 0)
            if img is None:
                print("I couldn't find an image for " + englishWord)
                continue

            self.thumbifyAndSave(englishWord, img)

            print(englishWord)
        
        print("I'm finished downloading thumbnails")

    @staticmethod
    def thumbifyAndSave(word, img):
        if img is None or word is "":
            print("Cannot save empty image or with empty file names")
            return

        # Convert the image into a thumbnail
        size = 256, 256
        img.thumbnail(size, Image.ANTIALIAS)
        
        # Save the thumbnail
        imageFilename = "../foodThumbnails/" + word + ".jpg"
        img.save(imageFilename, "JPEG")

    def getImageUrlForWord(self, word, retryTime):
        #consider prefacing word with 'edible'
        headers = {"Ocp-Apim-Subscription-Key" : self.subscriptionKey}
        params  = {"q": word}

        try:
            response = requests.get(search_url, headers=headers, params=params)
            response.raise_for_status()
            search_results = response.json()
            return search_results["value"][retryTime]["contentUrl"]
        except requests.exceptions.HTTPError:
            print("Could not find results for " + word)
            return ""

    def getImageForWord(self, word, retryTime):
        url = self.getImageUrlForWord(word, retryTime)
        img = None
        try:
            # Download the image
            r = requests.get(url)
            img = Image.open(BytesIO(r.content))
        except OSError:
            # This is okay, we'll just try another one
            print(url + " could not be downloaded.")

        return img

    def getNextImage(self, word, retryTime):
        img = self.getImageForWord(word, retryTime)
        while img is None and retryTime < maxTries:
            retryTime += 1
            img = self.getImageForWord(word, retryTime)

        return img, retryTime


if __name__ == '__main__':
    ImageDownloader().main("")