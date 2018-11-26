import sys, textwrap
from openpyxl import load_workbook
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

thismodule = sys.modules[__name__]

# consts
#Width and height are determined as half A4 paper at 300 dpi
thismodule.imageWidth = 2480
thismodule.imageHeight = 1754
thismodule.horizontal_padding = 50
thismodule.line_spacing_height = 100
thismodule.maxfontsize = 400
thismodule.idealfontsize = thismodule.maxfontsize
thismodule.fontlocation = "/Library/Fonts/Arial Unicode.ttf"
thismodule.thumbnailsize = (512, 512)

class SpreadsheetWrangler():

    @staticmethod    
    # Creates a dictionary of englishWord: [translatedWord, translatedWord, translatedWord]
    def build_translations_dict (spreadsheetLocation):
        workbook = load_workbook(filename = spreadsheetLocation, read_only=True)
        worksheet = workbook["translations"]

        dict = {}
        
        rows = list(worksheet.rows)
        for row in rows[1:-1]: #start at 1 to skip the header
            firstCell = True
            englishWord = ""
            translations = []
            for cell in row:
                if firstCell:
                    englishWord = cell.value
                    firstCell = False
                else:
                    translations.append(cell.value)

            if englishWord is None: #it's possible to have blank lines
                print("I can't add none to the dictionary!")
                print(translations)
            else:
                dict[englishWord] = translations
        return dict

    @staticmethod
    def get_lists_of_words_per_language(spreadsheetLocation):
        workbook = load_workbook(filename = spreadsheetLocation, read_only=True)
        worksheet = workbook["translations"]

        result = [[], [], [], []]

        rows = list(worksheet.rows)
        for row in rows[1:-1]: #start at 1 to skip the header
            index = 0
            for cell in row:
                if cell.value is not None:
                    result[index].append(cell.value)
                index += 1

        return result

class FinalImageCreater():

    translationsDict = {}
    
    def main(self, spreadsheetLocation):   
    
        if spreadsheetLocation == "":
            spreadsheetLocation = "../translatedWords.xlsx"
        
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
            filepath = "../foodThumbnails/" + inputWord + ".jpg"
            if not Path(filepath).is_file():
                filepath = "../foodThumbnails/" + inputWord + ".png"
                if not Path(filepath).is_file():
                    print ("Could not find an appropriate thumbnail for " + inputWord)
                    filepath = None

            # Handle printing the thumbnail if there is one
            if filepath is None:
                foodThumbnailImage = None
                thumbnailWidth, thumbnailHeight = 0,0 
                left_side_of_thumbnail = thismodule.imageWidth
            else: 
                foodThumbnailImage = Image.open(filepath)
                # Ensure the thumbnail is actually thumbnail size
                foodThumbnailImage.thumbnail(thismodule.thumbnailsize, Image.ANTIALIAS)
                # Get the dimensions for the thumbnail
                thumbnailWidth, thumbnailHeight = foodThumbnailImage.size
                left_side_of_thumbnail = thismodule.imageWidth - thumbnailWidth - (thismodule.horizontal_padding * 2)
                # Paste the thumbnail into the image
                thumbnail_offset = left_side_of_thumbnail, int((thismodule.imageHeight/2) - (thumbnailHeight/2)) # on the right, vertically centered
                outputImage.paste(foodThumbnailImage, thumbnail_offset)

            # The text has a horizontal padding at its left, so can't take up all the space before the thumbnail
            textwidth = left_side_of_thumbnail - thismodule.horizontal_padding 

            # Calculate the starting point of the text, so that it'll be vertically centered
            thismodule.idealfontsize = FontManipulator.find_font_size_to_fit_height(wordsToPrint, thismodule.imageHeight, thismodule.fontlocation, thismodule.maxfontsize)
            totalHeight = FontManipulator.calculate_total_text_height(wordsToPrint, textwidth, thismodule.fontlocation)
            word_y_pos = int((thismodule.imageHeight - totalHeight) / 2) # e.g. (1754 - 1500)/2 = start at 177

            # Print each word onto the image
            for word in wordsToPrint:
                fontsize = FontManipulator.find_font_size_to_fit_width(word, textwidth, thismodule.fontlocation, thismodule.idealfontsize)
                font = ImageFont.truetype(thismodule.fontlocation, fontsize)
                _, h = FontManipulator.get_font_with_offset(font, word)
                imageDrawer.text((thismodule.horizontal_padding, word_y_pos), word, font=font, fill=(0, 0, 0))
                word_y_pos += h + thismodule.line_spacing_height

            # Save off the image
            outputImage.save("../images/" + inputWord + ".png")
            
            print(inputWord)
        print("I'm finished creating output images")
            
class FontManipulator():
    @staticmethod
    def get_font_with_offset(font, text):
        return map(sum, zip(font.getsize(text), font.getoffset(text)))

    @staticmethod
    def find_font_size_to_fit_height(lines, height, font_location, max_size):
        # If we have to fit 5 lines in 2000 pixels then we have to fit 1 line in 400, so let's just calculate the max size to do that
        height /= len(lines)

        minfontsize = max_size
        for line in lines:
            linesize = FontManipulator.find_font_size_to_fit(line, height - thismodule.line_spacing_height, font_location, max_size, False)
            if linesize < minfontsize:
                minfontsize = linesize

        return minfontsize

    @staticmethod
    def find_font_size_to_fit_width(text, width, font_location, max_size):
        return FontManipulator.find_font_size_to_fit(text, width, font_location, max_size, True)

    @staticmethod
    def find_font_size_to_fit(text, fit_value, font_location, max_size, is_width):
        # Maybe it's already perfect
        font = ImageFont.truetype(font_location, max_size)
        w, h = FontManipulator.get_font_with_offset(font, text)
        if (is_width):
            result = w
        else:
            result = h

        if (result < fit_value):
            return max_size

        # If not, we do a binary search
        size = max_size
        upper_bound = max_size
        lower_bound = 0
        upper_bound_result = result

        while True:
            font = ImageFont.truetype(font_location, size)
            w, h = FontManipulator.get_font_with_offset(font, text)
            if (is_width):
                result = w
            else:
                result = h
            # If we find the perfect match, return it
            if result == fit_value:
                return size
            # If we blew over the top (say it was 74, and we tried a font size 49 and got 73, and font size 50 and got 75, we'd return the 73)
            elif result > upper_bound_result:
                return lower_bound
            # Business as usual - we have width 74, we got width 50, let's try a bigger font
            elif result > fit_value:
                upper_bound = size
                upper_bound_result = result
            # Business as usual - we have width 74, we got width 100, so let's try a smaller font
            else:
                lower_bound = size
            prevsize = size
            size = lower_bound + ((upper_bound - lower_bound) / 2)
            size = int(size)
            # Don't want to get caught inf looping
            if size == prevsize:
                return lower_bound

    @staticmethod    
    # Calculates the total text height for a list of words
    def calculate_total_text_height(list, width, font_location):
        totalH = 0
        for line in list:
            fontsize = FontManipulator.find_font_size_to_fit_width(line, width, font_location, thismodule.idealfontsize)
            font = ImageFont.truetype(font_location, fontsize)
            _, h = FontManipulator.get_font_with_offset(font, line)
            totalH += h + thismodule.line_spacing_height
        return totalH - thismodule.line_spacing_height # we don't need line spacing after the final word
        
if __name__ == '__main__':
    FinalImageCreater().main("")