import sys
from os.path import join
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from spreadsheetWrangler import SpreadsheetWrangler
from fontManipulator import FontManipulator

thismodule = sys.modules[__name__]

# consts
#Width and height are determined as half A4 paper at 300 dpi
thismodule.imageWidth = 2480
thismodule.imageHeight = 1754
thismodule.horizontalPadding = 50
thismodule.lineSpacingHeight = 100
thismodule.maxFontSize = 200
thismodule.idealFontSize = thismodule.maxFontSize
thismodule.fontLocation = "NotoSansCJKsc-Light.otf"
thismodule.thumbnailSize = (512, 512)

class FinalImageCreater():

    translationsDict = {}
    
    def main(self, spreadsheetLocation):           
        self.translationsDict = SpreadsheetWrangler.build_translations_dict(spreadsheetLocation)

        print("I'll print each word when I finish creating the output image for it")

        for inputWord, translatedWords in self.translationsDict.items():
            if inputWord is None:
                continue

            # Arrange the words into a nice list
            wordsToPrint = translatedWords
            wordsToPrint.insert(0, inputWord)

            # Draw out the white background + the word we translated
            outputImage = Image.new('RGB', (thismodule.imageWidth, thismodule.imageHeight), color = 'white')
            imageDrawer = ImageDraw.Draw(outputImage)            

            # Try to find the thumbnail for this word
            filepath = self.try_get_filepath_for_thumbnail(inputWord)

            # Handle printing the thumbnail if there is one
            if filepath is None:
                foodThumbnailImage = None
                thumbnailWidth, thumbnailHeight = 0,0 
                leftSideOfThumbnail = thismodule.imageWidth
            else: 
                foodThumbnailImage = Image.open(filepath)
                # Ensure the thumbnail is actually thumbnail size
                foodThumbnailImage.thumbnail(thismodule.thumbnailSize, Image.ANTIALIAS)
                # Get the dimensions for the thumbnail
                thumbnailWidth, thumbnailHeight = foodThumbnailImage.size
                leftSideOfThumbnail = thismodule.imageWidth - thumbnailWidth - thismodule.horizontalPadding
                # Paste the thumbnail into the image
                thumbnailOffset = leftSideOfThumbnail, int((thismodule.imageHeight/2) - (thumbnailHeight/2)) # on the right, vertically centered
                outputImage.paste(foodThumbnailImage, thumbnailOffset)

            # The text has a horizontal padding at its left and right, so can't take up all the space before the thumbnail
            textWidth = leftSideOfThumbnail - (thismodule.horizontalPadding  * 2)

            # Calculate the starting point of the text, so that it'll be vertically centered
            thismodule.idealfontsize = FontManipulator.find_font_size_to_fit_height(wordsToPrint, thismodule.imageHeight, thismodule.fontLocation, thismodule.maxFontSize, thismodule.lineSpacingHeight)
            totalHeight = FontManipulator.calculate_total_text_height(wordsToPrint, textWidth, thismodule.fontLocation, thismodule.idealFontSize, thismodule.lineSpacingHeight)
            word_y_pos = int((thismodule.imageHeight - totalHeight) / 2) # e.g. (1754 - 1500)/2 = start at 177

            # Print each word onto the image
            for word in wordsToPrint:
                fontsize = FontManipulator.find_font_size_to_fit_width(word, textWidth, thismodule.fontLocation, thismodule.idealFontSize)
                font = ImageFont.truetype(thismodule.fontLocation, fontsize)
                _, h = FontManipulator.get_font_with_offset(font, word)
                imageDrawer.text((thismodule.horizontalPadding, word_y_pos), word, font=font, fill=(0, 0, 0))
                word_y_pos += h + thismodule.lineSpacingHeight

            # Save off the image
            outputImage.save(join(join("..", "images"), inputWord  + ".png"))

            print(inputWord)
        print("I'm finished creating output images")
		

    # try to find an image for the thumbnail - tries jpg and png. doesn't do anything with casing
    # if it can't find it, it returns empty string
    @staticmethod
    def try_get_filepath_for_thumbnail(word):
        # Try to come up with an appropriate image path
        filepath = join("..", "foodThumbnails")
        filepath = join(filepath, word + ".jpg")	
        if not Path(filepath).is_file():
            filepath = join("..", "foodThumbnails")
            filepath = join(filepath, word + ".png")
            if not Path(filepath).is_file():
                print ("Could not find an appropriate thumbnail for " + word)
                filepath = ""

        return filepath

if __name__ == '__main__':
    FinalImageCreater().main(join("..", "translatedWords.xlsx"))
