from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import AliasProperty, StringProperty, NumericProperty
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.recycleview import RecycleView
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from pathlib import Path

from findAndSaveImages import ImageDownloader
from outputImages import FinalImageCreater, SpreadsheetWrangler
from outputTranslations import WordTranslator

class Spreadsheet():
    def __init__(self):
        self.rows = []

    def getInputWords(self):
        inputWords = []
        for row in self.rows:
            inputWords.append(row.inputWord)
        return inputWords

    def build_dict(self):
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
        self.deleteButton = None

        super().__init__(**kwargs)

        # Add the english word column
        inputWordWidget = TextInput(text=self.inputWord, multiline=False)
        inputWordWidget.bind(text=self.on_input_word_edit)
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
            textInput.bind(text=self.on_translated_word_edit)
            self.gridLayout.add_widget(textInput)
            self.instanceToValue[textInput] = self.outputWordsList[i]

        # Add in the thumbnail cell
        newThumb = Thumbnail() #size_hint=(None, None), width=700, height=400

        newThumb.name = self.inputWord
        newThumb.filepath = self.imgFilepath
        self.gridLayout.add_widget(newThumb)

        deleteButton = Button()
        deleteButton.text = "⌫"
        deleteButton.background_color = (0.75, 0, 0, 1)
        deleteButton.bind(on_press=self.delete_this_row)
        deleteButton.size_hint = (None, None)
        deleteButton.size = self.size
        self.gridLayout.add_widget(deleteButton)

    def delete_this_row(self, instance):
        Translator._instance.remove_spreadsheet_row(self)

    def on_input_word_edit(self, instance, value):
        self.inputWord = value

    def on_translated_word_edit(self, instance, value):
        self.instanceToValue[instance] = value

class Thumbnail(Widget):
    image = None
    name = StringProperty("")
    filepath = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tryTime = 0
        Clock.schedule_interval(self.reload_img, 10)

    def reload_img(self, dt):
        self.image.reload()

    def download_new_thumb(self):
        (img, self.tryTime) = ImageDownloader().get_next_image(self.name, self.tryTime + 1)
        ImageDownloader.thumbify_and_save(self.name, img)
        self.reload_img(0)

    def download_prev_thumb(self):
        (img, self.tryTime) = ImageDownloader().get_prev_image(self.name, self.tryTime - 1)
        ImageDownloader.thumbify_and_save(self.name, img)
        self.reload_img(0)

class InputWordsPopup(Popup):
    def add_words(self, inputWords):
        inputWords = inputWords.split("\n")
        for inputWord in inputWords:
            Translator._instance.create_spreadsheet_row(inputWord, ["", "", ""], "")
            self.dismiss()

class Translator(Widget):
    _instance = None
    _spreadsheet = Spreadsheet()
    _spreadsheetViewer = None 

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if Path("../translatedWords.xlsx").is_file():
            self.import_from_spreadsheet()
            self.create_empty_spreadsheet_row()

    def paste_input_words(self):
        popup = InputWordsPopup(title='One food item per line')
        popup.open()

    def generate_translations(self):
        inputWords = self._spreadsheet.getInputWords()
        self.reset_spreadsheet()
        translationsDict = WordTranslator().generate_translations_dict(inputWords)
        ImageDownloader().get_images_for_words(list(translationsDict.keys()))
        self.create_spreadsheet_rows_from_dict(translationsDict)

    # takes contents on screen and creates a spreadsheet
    def export_to_spreadsheet(self):
        WordTranslator().write_dict_to_spreadsheet(self._spreadsheet.build_dict())

    # reads contents of spraedsheet and updates contents on screen
    def import_from_spreadsheet(self):    
        self.create_spreadsheet_rows_from_dict(SpreadsheetWrangler.build_translations_dict("../translatedWords.xlsx"))

    def create_empty_spreadsheet_row(self):
        #TODO: hardcode the correct number of output words, not just arbitrarily 3
        self.create_spreadsheet_row("", ["", "", ""], "")

    def create_spreadsheet_row(self, inputWord, outputWords, imgFilePath):
        newRow = SpreadsheetRow(parentSheet=self._spreadsheet, inputWord=inputWord, outputWords=outputWords, imgFilepath=imgFilePath)
        self._spreadsheetViewer.add_widget(newRow)

    def remove_spreadsheet_row(self, row):
        self._spreadsheetViewer.remove_widget(row)
        self._spreadsheet.rows.remove(row)

    def output_images(self):
        FinalImageCreater().main("")

    def create_spreadsheet_rows_from_dict(self, translationsDict):
        self.reset_spreadsheet()
        for inputWord, outputWords in translationsDict.items():
            # Try to come up with an appropriate image path
            filepath = "../foodThumbnails/" + inputWord + ".jpg"
            if not Path(filepath).is_file():
                filepath = "../foodThumbnails/" + inputWord + ".png"
                if not Path(filepath).is_file():
                    print ("Could not find an appropriate thumbnail for " + inputWord)
                    filepath = ""

            # Add the row to the spreadsheet viewer
            newRow = SpreadsheetRow(parentSheet=self._spreadsheet, inputWord=inputWord, outputWords=outputWords, imgFilepath=filepath)
            self._spreadsheetViewer.add_widget(newRow)

    def reset_spreadsheet(self):
        self._spreadsheetViewer.clear_widgets()
        self._spreadsheet.rows = []

class MainApp(App):
    def build(self):
        Window.maximize()
        return Translator()

if __name__ == '__main__':
    MainApp().run()