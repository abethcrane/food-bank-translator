from openpyxl import load_workbook
from PIL import Image, ImageDraw, ImageFont
import textwrap

# consts
imageWidth = 1400
padding = 50
lineSpacingHeight = 100

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
        arialUnicodeFont = ImageFont.truetype('/Library/Fonts/Arial Unicode.ttf', 100)

        print("I'll print each word when I finish creating the output image for it")

        for englishWord, translatedWords in self.translationsDict.items():
            if englishWord is None:
                continue

            print("Currently making an image for " + englishWord)
            # Open the thumbnail for this word and get the dimensions
            foodThumbnailImage = Image.open("../foodThumbnails/" + englishWord + ".jpg", "r")
            # TODO check if image exists!

            thumbnailWidth, thumbnailHeight = foodThumbnailImage.size
            
            leftSideOfImage = imageWidth - thumbnailWidth - (padding * 2)
            
            # Now figure out the text height so we can calculate our image height
            translationsToPrint = []
            translationsToPrint.append(WordWrapper.getWrappedLines(englishWord, leftSideOfImage, arialUnicodeFont))
            
            # Print all the words onto the slide
            for translatedWord in translatedWords:
                translationsToPrint.append(WordWrapper.getWrappedLines(translatedWord, leftSideOfImage, arialUnicodeFont))

            totalHeight = WordWrapper.calculateTotalTextHeight(translationsToPrint, arialUnicodeFont) + (lineSpacingHeight * (len(translationsToPrint) - 1)) # + spacing
            
            # Draw out the white background + the word we translated
            outputImage = Image.new('RGB', (imageWidth, totalHeight + (padding * 2)), color = 'white')
            imageDrawer = ImageDraw.Draw(outputImage)
            height = padding
            
            for translation in translationsToPrint:
                for line in translation:
                    w, h = arialUnicodeFont.getsize(line)
                    imageDrawer.text((padding, height), line, font=arialUnicodeFont, fill=(0, 0, 0))
                    height += h
                height += lineSpacingHeight
            
            # Paste in the thumbnail image
            offset = imageWidth - thumbnailWidth - padding, int((totalHeight/2) - (thumbnailHeight/2)) # on the right, vertically centered
            outputImage.paste(foodThumbnailImage, offset)
            
            # Save off the image
            outputImage.save("../images/" + englishWord + ".png")
            
            print(englishWord)
        print("I'm finished creating output images")
            
class WordWrapper():

    @staticmethod
    # Splts a line + word into whatever fits within width + a "-", and the remnants that didn't fit
    def splitWordToWidth(line, word, width, font):
        w, h =  font.getsize(line)
        
        while w > width:
            line, leftover = WordWrapper.splitContentToWidth(line, width, font)
            w, h =  font.getsize(leftover)

        dashWidth, h = font.getsize("-")
        width -= dashWidth

        line = line + " "
        returnWord = ""
        for char in word:
            w, h = font.getsize(line + char)
            if w > width:
                returnWord += char
            else:
                line = line + char

        line += "-"
        return line, returnWord
        
    @staticmethod
    # Splits a str up into a line that fits in width, and whatever didn't fit
    def splitContentToWidth(str, width, font):
        dashWidth, h = font.getsize("-")
        width -= dashWidth

        line = ""
        leftover = ""
        for char in str:
            w, h = font.getsize(line + char)
            if w > width:
                leftover += char
            else:
                line = line + char

        line += "-"
        return line, leftover
         
    @staticmethod  
    # Gets the wrapped lines for a str to fit into width
    def getWrappedLines(str, width, font):
        words = str.split(' ')
        total = 0
        line = ""
        lines = []
        
        # For each word, see if it can be added onto the line and still fit in the width
        for word in words:
            totalW, totalH = font.getsize(line)
            newW, newH = font.getsize(" " + word)
            
            if totalW + newW > width:
                # If it can't fit, split the word at whatever character is the last to fit
                line, leftover = WordWrapper.splitWordToWidth(line, word, width, font)
                lines.append(line)
                line = leftover
                
                # In case our leftover content was too big to fit on a line
                # We need to loop through until we have a leftover amount that can fit on a line
                lineW, lineH = font.getsize(line)
                while lineW > width:
                    line, leftover = WordWrapper.splitWordToWidth("", line, width, font)
                    lines.append(line)
                    line = leftover
                    lineW, lineH = font.getsize(line)
            else:
                # If it fits, add it the line with a space in front of it :)
                line = line + " " + word
        
        # Add back in the last line :)
        lines.append(line)

        return lines

    @staticmethod    
    # Calculates the total text height for a list of lists
    # e.g. [[line1, line2], [line1, line2, line3], [line1]]
    def calculateTotalTextHeight(listOfLists, font):
        totalH = 0
        for list in listOfLists:
            for line in list:
                w, h = font.getsize(line)
                totalH += h
        return totalH
        
        
if __name__ == '__main__':
    FinalImageCreater().main("")