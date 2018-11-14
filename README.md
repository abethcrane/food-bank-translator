# food-bank-translator
Takes in a list of output-languages, and a list of input-words (in English) and creates pngs with the translations

Written in Python3, using Pillow for images. Uses Microsoft Cognitive Services for the translation.

Still a WIP, working with <a href="http://www.pmfb.org/">a Seattle organization</a>.

Requirements:
- Python 3
- <a href="https://pillow.readthedocs.io">Pillow</a> (for creating images)
- <a href="https://openpyxl.readthedocs.io/">OpenPyXL</a> (for interacting with spreadsheets)
- <a href="http://docs.python-requests.org/en/master/">Requests</a> (for the bing image search code to work)
- <a href="https://kivy.org/doc/stable/gettingstarted/intro.html#">Kivy</a> (for the UI)
- An azure subscription key to use the translator api (https://azure.microsoft.com/en-us/services/cognitive-services/translator-text-api/)
- An azure subscription key to use Bing image search (https://azure.microsoft.com/en-us/services/cognitive-services/bing-image-search-api/)
- Arial (or swap the font to one you have)

To use gui:
<img src="https://github.com/abethcrane/food-bank-translator/blob/master/appScreenshot.png">
- Install kivy
- Run main.py

To use command line:
<img src="https://github.com/abethcrane/food-bank-translator/blob/master/commandLineScreenshot.png">
- Ensure you have a folder called **foodThumbnails** and one called **images**, in the same dir as your input files (sibling dirs with **src**).
- Run `python3 getLanguageCodes.py` (I've included the results here in **languageCodes.txt**) to see the language codes available
- Modify the **toLanguages.txt** file to include whichever languages you desire
- Modify the **words.txt** to include the words you'd like to translate
- Create a file called translatorSubscriptionKey.txt and enter your azure translation subscription key in
- Run `python3 outputTranslations.py` - this will open the words and toLangugaes files and output a spreadsheet of translations for each word
- Open the spreadsheet **translatedWords.xlsx**
- Modify any translations you like
- Run `python3 findAndSaveImages.py` - this will open the spreadsheet and download an image for each english word
- Open the **foodThumbnails** folder and check the images. If any images aren't suitable, replace them with new ones of the same name
- Run `python3 outputImages.py` - this will open the spreadsheet and output an image for each word, with the translations + thumbnail image

Quirks:
- Currently expects a newline at the start of the toLanguages file
- Currently assumes foodThumbnails images are max 256x256 and with the same name (+casing) as the english word in the spreadsheet
- The main app assumes there are 4 languages (1 input + 3 output)
