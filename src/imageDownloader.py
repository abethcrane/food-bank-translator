import json, os, requests, sys, urllib.parse, uuid
from io import BytesIO
from os.path import join
from PIL import Image
from socket import gaierror
from spreadsheetWrangler import SpreadsheetWrangler

thismodule = sys.modules[__name__]

thismodule.searchUrl = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"
thismodule.maxTries = 5
thismodule.resultsPerQuery = 35
thismodule.thumbnailSize = (512, 512)
thismodule.scriptdir = os.path.dirname(os.path.realpath(__file__))
thismodule.parentdir = join(thismodule.scriptdir, "..")

class ImageDownloaderInterface():
    """Abstract class/interface for ImageDownloader, so that we 
    can stub it for unit testing - not requiring the subscriptionKey"""
    def aMethod( self ):
        raise NotImplementedError( "Should have implemented this" )


class ImageDownloader():
    def __init__(self):
        subscriptionKeysFolder = join(thismodule.parentdir, "subscriptionKeys")
        subscriptionKeyPath = join(subscriptionKeysFolder, "imageSubscriptionKey.txt")
        self.subscriptionKey = open(subscriptionKeyPath).read()

    def __main(self, spreadsheetLocation, outputThumbnailsFolder):
        print("I'll print each word when I finish downloading a thumbnail for it")

        englishWords = SpreadsheetWrangler.get_english_words(spreadsheetLocation)
        for englishWord in englishWords:
            (img, _) = self.get_next_image(englishWord, 0)
            if img is None:
                print("I couldn't find an image for", englishWord)
                continue

            self.thumbify_and_save(englishWord, img, outputThumbnailsFolder)

            print(englishWord)
        
        print("I'm finished downloading thumbnails")

    def get_images_for_words(self, words, outputThumbnailsFolder):
        print ("I'm getting the images for some words - I'll print each one's name as I go")
        for word in words:
            if word is None or word is "":
                continue

            (img, _) = self.get_next_image(word, 0)
            if img is None:
                print("I couldn't find an image for", word)
                continue

            self.thumbify_and_save(word, img, outputThumbnailsFolder)
            print(word)

    @staticmethod
    def thumbify_and_save(word, img, outputThumbnailsFolder):
        if not os.path.exists(outputThumbnailsFolder):
            os.makedirs(outputThumbnailsFolder)
    
        if img is None or word is "":
            print("Cannot save empty image or with empty file names")
            return

        # Convert the image into a thumbnail
        img.thumbnail(thismodule.thumbnailSize, Image.ANTIALIAS)
        
        # Save the thumbnail
        imageFilename = join(outputThumbnailsFolder, word + ".jpg")
        img.convert('RGB').save(imageFilename, "JPEG")

    def get_next_image(self, word, n):
        if (n < 0):
            n = 0
        img = self.__get_nth_image_for_word(word, n)
        retryTime = 0
        while img is None and retryTime < thismodule.maxTries:
            retryTime += 1
            n += 1
            img = self.__get_nth_image_for_word(word, n)

        return img, n

    def get_prev_image(self, word, n):
        if (n < 0):
            n = thismodule.resultsPerQuery - 1
        img = self.__get_nth_image_for_word(word, n)
        retryTime = 0
        while img is None and retryTime < thismodule.maxTries and n >= 0:
            retryTime += 1
            n -= 1
            img = self.__get_nth_image_for_word(word, n)

        return img, n

    def __get_nth_image_for_word(self, word, n):
        url = self.__get_image_url_for_word(word, n)
        img = None
        try:
            # Download the image
            r = requests.get(url)
            img = Image.open(BytesIO(r.content))
        except OSError:
            # This is okay, we'll just try another one
            print(url, "could not be downloaded.")

        return img

    def __get_image_url_for_word(self, word, retryTime):
        #consider prefacing word with 'edible'
        headers = {"Ocp-Apim-Subscription-Key" : self.subscriptionKey}
        params  = {"q": word}

        try:
            response = requests.get(thismodule.searchUrl, headers=headers, params=params)
            response.raise_for_status()
            search_results = response.json()
            if len(search_results["value"]) > retryTime:
                return search_results["value"][retryTime]["contentUrl"]
            else:
                print("Oops, too many retries for " + word)
                return ""
        except (requests.exceptions.HTTPError, gaierror, requests.exceptions.ConnectionError):
            print("Could not find results for " + word)
            return ""

if __name__ == '__main__':
    outputFolder = join(thismodule.parentdir, "output")
    ImageDownloader().__main(join(outputFolder, "translatedWords.xlsx"), join(outputFolder, "foodThumbnails"))