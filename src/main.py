from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
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

    def __init__(self):
        self.rows = []

    def getInputWords(self):
        inputWords = []
        for row in self.rows:
            inputWords.append(row.inputWord)
        return inputWords

    def buildDict(self):
        translationsDict = {}
        for row in self.rows:
            translatedWords = []
            for instance, word in row.instanceToValue.items():
                translatedWords.append(word)
            translationsDict[row.inputWord] = translatedWords

        return translationsDict

class SpreadsheetRow(Widget):

    numOutputLangs = NumericProperty(3)

    def __init__(self, **kwargs):
        self.gridLayout = None
        self.outputWordsList = []
        self.imgFilepath = StringProperty("")
        self.inputWord = StringProperty("")
        self.parentSheet = None
        self.instanceToValue = {}
        
        self.parentSheet = kwargs.pop("parentSheet")
        self.inputWord = kwargs.pop("inputWord")
        self.outputWordsList = kwargs.pop("outputWords")
        self.imgFilepath = kwargs.pop("imgFilepath")

        super().__init__(**kwargs)

        # Add the english word column
        inputWordWidget = TextInput(text=self.inputWord, multiline=False)
        inputWordWidget.bind(text=self.onInputWordEdit)
        self.gridLayout.add_widget(inputWordWidget)

        # Add on a text input for each output language
        if self.parentSheet is not None:
            self.parentSheet.rows.append(self)
        else:
            print("my parent sheet was none, weird")

        self.numOutputLangs = len(self.outputWordsList)

        # Create input cells for each output language
        for i in range (0, self.numOutputLangs):
            textInput = TextInput(text=self.outputWordsList[i], multiline=False)
            textInput.bind(text=self.onTranslatedWordEdit)
            self.gridLayout.add_widget(textInput)
            self.instanceToValue[textInput] = self.outputWordsList[i]

        # Add in the thumbnail cell
        newThumb = Thumbnail() #size_hint=(None, None), width=700, height=400

        newThumb.name = self.inputWord
        newThumb.filepath = self.imgFilepath
        self.gridLayout.add_widget(newThumb)

    def onInputWordEdit(self, instance, value):
        self.inputWord = value

    def onTranslatedWordEdit(self, instance, value):
        self.instanceToValue[instance] = value
        print(self.instanceToValue)

class Thumbnail(Widget):
    image = None
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if Path("../translatedWords.xlsx").is_file():
            self.ImportFromSpreadsheet()
            self.CreateEmptySpreadsheetRow()

    def OutputImages(self):
        FinalImageCreater().main("")

    def GenerateTranslations(self):
        inputWords = self.spreadsheet.getInputWords()
        self.ResetSpreadsheet()
        translationsDict = WordTranslator().generateTranslationsDict(inputWords)
        self.CreateSpreadsheetRows(translationsDict)
        ImageDownloader().getImagesForWords(list(translationsDict.keys()))


    # takes contents on screen and creates a spreadsheet
    def ExportToSpreadsheet(self):
        WordTranslator().writeDictToSpreadsheet(self.spreadsheet.buildDict())

    # reads contents of spraedsheet and updates contents on screen
    def ImportFromSpreadsheet(self):    
        self.CreateSpreadsheetRows(SpreadsheetWrangler.buildTranslationsDict("../translatedWords.xlsx"))

    def CreateEmptySpreadsheetRow(self):
        #TODO: hardcode the correct number of output words, not just arbitrarily 3
        newRow = SpreadsheetRow(parentSheet=self.spreadsheet, inputWord="", outputWords=["", "", ""], imgFilepath="")
        self.spreadsheetViewer.add_widget(newRow)

    def CreateSpreadsheetRows(self, translationsDict):
        self.ResetSpreadsheet()
        for inputWord, outputWords in translationsDict.items():
            # Try to come up with an appropriate image path
            filepath = "../foodThumbnails/" + inputWord + ".jpg"
            if not Path(filepath).is_file():
                filepath = "../foodThumbnails/" + inputWord + ".png"
                if not Path(filepath).is_file():
                    continue

            # Add the row to the spreadsheet viewer
            newRow = SpreadsheetRow(parentSheet=self.spreadsheet, inputWord=inputWord, outputWords=outputWords, imgFilepath=filepath)
            self.spreadsheetViewer.add_widget(newRow)

    def ResetSpreadsheet(self):
        self.spreadsheetViewer.clear_widgets()
        self.spreadsheet.rows = []

class MainApp(App):
    def build(self):
        Window.maximize()
        return Translator()

if __name__ == '__main__':
    MainApp().run()