from openpyxl import load_workbook
from PIL import Image, ImageDraw, ImageFont

translationsDict = {}

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

buildTranslationsDict()
fnt = ImageFont.truetype('/Library/Fonts/Arial Unicode.ttf', 100)

for englishWord, translatedWords in translationsDict.items():
    # Draw out the white background + the word we translated
    img = Image.new('RGB', (1024, 720), color = 'white')
    d = ImageDraw.Draw(img)
    height = 10
    d.text((10,height), englishWord, font=fnt, fill=(0, 0, 0))
    height += 200
    
    # Print all the words onto the slide
    for translatedWord in translatedWords:
        d.text((10,height), translatedWord, font=fnt, fill=(0, 0, 0))
        height += 100
        
    # Save off the image
    img.save("images/" + englishWord + ".png")
