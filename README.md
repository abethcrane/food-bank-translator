# food-bank-translator
Takes in a list of output-languages, and a list of input-words (in English) and creates pngs with the translations

Written in Python3, using Pillow for images. Uses Microsoft Cognitive Services for the translation.

Still a WIP, working with <a href="http://www.pmfb.org/">a Seattle organization</a>.

Requirements:
- Python 3
- Pillow (for creating images)
- An azure subscription key (to use the translator api https://azure.microsoft.com/en-us/services/cognitive-services/translator-text-api/)
- Arial (or swap the font to one you have)

To use:
- Run the getLanguageCodes.py script (I've included the results here in languageCodes.txt) to see the language codes available
- Modify the toLanguages.txt file to include whichever languages you desire
- Modify the words.txt to include the words you'd like to translate
- Create a file called subscriptionKey.txt and enter your azure subscription key in
- Run translator.py in python3
- Results will appear in the images folder

Quirks:
- Currently expects a newline at the start of the toLanguages file
