# food-bank-translator
Takes in a list of output-languages, and a list of input-words (in English) and creates pngs with the translations

Written in Python3, using Pillow for images. Kivy for UI. Uses Microsoft Cognitive Services for the translation.

Still a WIP, working with <a href="http://www.pmfb.org/">a Seattle organization</a>.

<h2>Requirements</h2>
<ul>Python 3</ul>
<ul><a href="https://pillow.readthedocs.io">Pillow</a> (for creating images)</ul>
<ul><a href="https://openpyxl.readthedocs.io/">OpenPyXL</a> (for interacting with spreadsheets)</ul>
<ul><a href="http://docs.python-requests.org/en/master/">Requests</a> (for the bing image search code to work)</ul>
<ul><a href="https://kivy.org/doc/stable/gettingstarted/intro.html#">Kivy</a> (for the UI)</ul>
<ul><a href="https://docs.pytest.org/en/latest/getting-started.html#getstarted">Pytest</a> (for testing)</ul>
<ul>An azure subscription key to use the <a href="https://azure.microsoft.com/en-us/services/cognitive-services/translator-text-api/">Bing translator api</a></ul>
<ul>An azure subscription key to use <a href="https://azure.microsoft.com/en-us/services/cognitive-services/bing-image-search-api/">Bing image search</a></ul>

<h2>Usage instructions</h2>
<h3>Gui</h3>
<img src="https://raw.githubusercontent.com/abethcrane/food-bank-translator/master/appScreenshot.png">
<ul>Install kivy</ul>
<ul>Run <code>python3 main.py</code></ul>

<h3>To use command line</h3>
<img src="https://raw.githubusercontent.com/abethcrane/food-bank-translator/master/commandLineScreenshot.png">
<ul>Ensure you have a folder called <em>output/foodThumbnails</em> and one called <em>output/images</em> (where output is a sibling dir or <em>src</em>).</ul>
<ul>Run <code>python3 getLanguageCodes.py</code> (I've included the results here in <em>languageCodes.txt</em>) to see the language codes available</ul>
<ul>Modify the <em>input/toLanguages.txt</em> file to include whichever languages you desire</ul>
<ul>Modify the <em>input/words.txt</em> file to include the words you'd like to translate</ul>
<ul>Create a file called <em>subscriptionKeys/translatorSubscriptionKey.txt</em> and enter your azure translation subscription key in</ul>
<ul>Run <code>python3 wordTranslator.py</code> - this will open the words.txt and toLanguages.txt files and output a spreadsheet of translations for each word</ul>
<ul>Open the spreadsheet <em>output/translatedWords.xlsx</em></ul>
<ul>Modify any translations you like</ul>
<ul>Run <code>python3 imageDownloader.py</code> - this will open the spreadsheet and download an image for each english word</ul>
<ul>Open the <em>foodThumbnails</em> folder and check the images. If any images aren't suitable, replace them with new ones of the same name</ul>
<ul>Run <code>python3 finalImageCreator.py</code> - this will open the spreadsheet and output an image for each word, with the translations + thumbnail image</ul>

<h2>Quirks</h2>
<ul>Currently expects a newline at the start of the toLanguages file</ul>
<ul>Currently assumes foodThumbnails images are max 512x512 and with the same name (+casing) as the english word in the spreadsheet</ul>
<ul>The main app assumes there are 4 languages (1 input + 3 output)</ul>

<h2>Authors and Contributors</h2>
@abethcrane wrote this in late 2018-early 2019 after volunteering with a foodbank and being asked to manually create these images
