from openpyxl import load_workbook
from PIL import Image, ImageDraw, ImageFont
import textwrap

# consts
imageWidth = 1400
padding = 50
lineSpacingHeight = 100

translationsDict = {}

# Creates a dictionary of englishWord: [translatedWord, translatedWord, translatedWord]
def buildTranslationsDict ():
    workbook = load_workbook(filename = "translatedWords.xlsx", read_only=True)
    worksheet = workbook["translations"]
    
    rows = list(worksheet.rows)
    skipped = False
    for row in worksheet.rows:
        # first row is the title, so skip that
        if not skipped:
            skipped = True
            continue
        
        firstCell = True
        englishWord = ""
        translations = []
        for cell in row:
            if firstCell:
                englishWord = cell.value
                firstCell = False
            else:
                translations.append(cell.value)
        translationsDict[englishWord] = translations
        
# Splts a line + word into whatever fits within width + a "-", and the remnants that didn't fit
def splitWordToWidth(line, word, width):
    w, h =  arialUnicodeFont.getsize(line)
    
    while w > width:
        line, leftover = splitContentToWidth(line, width)
        w, h =  arialUnicodeFont.getsize(leftover)

    dashWidth, h = arialUnicodeFont.getsize("-")
    width -= dashWidth

    line = line + " "
    returnWord = ""
    for char in word:
        w, h = arialUnicodeFont.getsize(line + char)
        if w > width:
            returnWord += char
        else:
            line = line + char

    line += "-"
    return line, returnWord
    
# Splits a str up into a line that fits in width, and whatever didn't fit
def splitContentToWidth(str, width):
    dashWidth, h = arialUnicodeFont.getsize("-")
    width -= dashWidth

    line = ""
    leftover = ""
    for char in str:
        w, h = arialUnicodeFont.getsize(line + char)
        if w > width:
            leftover += char
        else:
            line = line + char

    line += "-"
    return line, leftover
        
# Gets the wrapped lines for a str to fit into width
def getWrappedLines(str, width):
    words = str.split(' ')
    total = 0
    line = ""
    lines = []
    
    # For each word, see if it can be added onto the line and still fit in the width
    for word in words:
        totalW, totalH = arialUnicodeFont.getsize(line)
        newW, newH = arialUnicodeFont.getsize(" " + word)
        
        if totalW + newW > width:
            # If it can't fit, split the word at whatever character is the last to fit
            line, leftover = splitWordToWidth(line, word, width)
            lines.append(line)
            line = leftover
            
            # In case our leftover content was too big to fit on a line
            # We need to loop through until we have a leftover amount that can fit on a line
            lineW, lineH = arialUnicodeFont.getsize(line)
            while lineW > width:
                line, leftover = splitWordToWidth("", line, width)
                lines.append(line)
                line = leftover
                lineW, lineH = arialUnicodeFont.getsize(line)
        else:
            # If it fits, add it the line with a space in front of it :)
            line = line + " " + word
    
    # Add back in the last line :)
    lines.append(line)

    return lines
    
# Calculates the total text height for a list of lists
# e.g. [[line1, line2], [line1, line2, line3], [line1]]
def calculateTotalTextHeight(translations):
    totalH = 0
    for translation in translations:
        for line in translation:
            w, h = arialUnicodeFont.getsize(line)
            totalH += h
    return totalH
    
    
## PROGRAM START ## 
    
buildTranslationsDict()
arialUnicodeFont = ImageFont.truetype('/Library/Fonts/Arial Unicode.ttf', 100)

print("I'll print each word when I finish creating the output image for it")

for englishWord, translatedWords in translationsDict.items():

    # Open the thumbnail for this word and get the dimensions
    foodThumbnailImage = Image.open("foodThumbnails/" + englishWord + ".jpg", "r")
    # TODO check if image exists!

    thumbnailWidth, thumbnailHeight = foodThumbnailImage.size
    
    leftSideOfImage = imageWidth - thumbnailWidth - (padding * 2)
    
    # Now figure out the text height so we can calculate our image height
    translationsToPrint = []
    translationsToPrint.append(getWrappedLines(englishWord, leftSideOfImage))
    
    # Print all the words onto the slide
    for translatedWord in translatedWords:
        translationsToPrint.append(getWrappedLines(translatedWord, leftSideOfImage))

    totalHeight = calculateTotalTextHeight(translationsToPrint) + (lineSpacingHeight * (len(translationsToPrint) - 1)) # + spacing
    
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
    outputImage.save("images/" + englishWord + ".png")
    
    print(englishWord)
