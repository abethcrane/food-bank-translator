from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import AliasProperty, StringProperty, NumericProperty
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from outputTranslations import WordTranslator
from outputImages import FinalImageCreater, SpreadsheetWrangler
from findAndSaveImages import ImageDownloader

class Spreadsheet():
    rows = []

    def getInputWords(self):
        inputWords = []
        for row in self.rows:
            inputWords.append(row.inputWord)
        return inputWords

    def buildDict(self):
        translationsDict = {}
        for row in self.rows:
            translationsDict[row.inputWord] = row.outputWordsList
        return translationsDict

class SpreadsheetRow(Widget):
    gridLayout = None
    numOutputLangs = NumericProperty(3)
    inputWord = StringProperty("")
    outputWordsList = []
    outputWordProperties = []
    imgFilepath = StringProperty("")
    parentSheet = None

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        # delay the end of the initialization to the next frame, once the widget are already created
        # and the properties properly initialized
        Clock.schedule_once(self.finish_init,0)

    def finish_init(self, dt):
        # Add on a text input for each output language
        print ("finishing init!")
        if self.parentSheet is not None:
            self.parentSheet.rows.append(self)

        self.numOutputLangs = len(self.outputWordsList)
        for i in range (0, self.numOutputLangs):
            #self.outputWordProperties.append(StringProperty(self.outputWordsList[i]))
            self.gridLayout.add_widget(TextInput(text=self.outputWordsList[i]))

        # Add in the thumbnail cell
        newThumb = Thumbnail()
        newThumb.name = self.inputWord
        newThumb.filepath = self.imgFilepath
        self.gridLayout.add_widget(newThumb)

        #self.bind words something something

class Thumbnail(Widget):
    image = None
    label = None
    name = StringProperty("")
    filepath = StringProperty("")
    tryTime = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.reloadImg, 10)

    def reloadImg(self, dt):
        self.image.reload()

    def DownloadNewThumb(self):
        (img, self.tryTime) = ImageDownloader().getNextImage(self.name, self.tryTime + 1)
        ImageDownloader.thumbifyAndSave(self.name, img)
        self.reloadImg(0)

    def DownloadPrevThumb(self):
        (img, self.tryTime) = ImageDownloader().getPrevImage(self.name, self.tryTime - 1)
        ImageDownloader.thumbifyAndSave(self.name, img)
        self.reloadImg(0)

class Translator(Widget):
    spreadsheet = Spreadsheet()
    spreadsheetViewer = None 

    lang1 = StringProperty("")
    lang2 = StringProperty("")
    lang3 = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if Path("../translatedWords.xlsx").is_file():
            self.ImportFromSpreadsheet()
            self.CreateEmptySpreadsheetRow()

    def OutputImages(self):
        FinalImageCreater().main("")

    def OutputTranslations(self):
        inputWords = ["apples", "bananas", "bread"]
        translations = WordTranslator().generateTranslationsDict(inputWords)
        self.lang1 = "\n".join(translations[0])
        self.lang2 = "\n".join(translations[1])
        self.lang3 = "\n".join(translations[2])

        ImageDownloader().main("")

    def GenerateTranslations(self):
        inputWords = self.spreadsheet.getInputWords()
        translationsDict = WordTranslator().generateTranslationsDict(inputWords)

        self.CreateSpreadsheetRows(translationsDict)

        ImageDownloader().main("")

    # takes contents on screen and creates a spreadsheet
    def ExportToSpreadsheet(self):
        WordTranslator().writeDictToSpreadsheet(self.spreadsheet.buildDict())

    # reads contents of spraedsheet and updates contents on screen
    def ImportFromSpreadsheet(self):    
        self.CreateSpreadsheetRows(SpreadsheetWrangler.buildTranslationsDict("../translatedWords.xlsx"))

    def CreateEmptySpreadsheetRow(self):
        self.spreadsheetViewer.data.append({"parentSheet": self.spreadsheet, "inputWord": "", 'outputWordsList': ["", "", ""], "imgFilepath": ""})

    def CreateSpreadsheetRows(self, translationsDict):
        self.spreadsheetViewer.data = []
    
        for inputWord, outputWords in translationsDict.items():
            print ("Creating spreadsheet row for " + inputWord)

            # Try to come up with an appropriate image path
            filepath = "../foodThumbnails/" + inputWord + ".jpg"
            if not Path(filepath).is_file():
                filepath = "../foodThumbnails/" + inputWord + ".png"
                if not Path(filepath).is_file():
                    continue

            # Add the row to the spreadsheet viewer
            self.spreadsheetViewer.data.append({"parentSheet": self.spreadsheet, "inputWord": inputWord, 'outputWordsList': outputWords, "imgFilepath": filepath})

class MainApp(App):
    def build(self):
        return Translator()

if __name__ == '__main__':
    MainApp().run()