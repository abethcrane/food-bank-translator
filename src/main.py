from os.path import join, isdir
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.recycleview import RecycleView
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from findAndSaveImages import ImageDownloader
from outputImages import FinalImageCreater, SpreadsheetWrangler
from outputTranslations import WordTranslator

class Preferences():
    importSpreadsheetPath = "."
    exportSpreadsheetPath = "../"
    inputLangName = "English"
    outputLangCodes = ["zh-Hans", "es", "vi"]
    outputLangNames = ["Simplified Chinese", "Spanish", "Vietnamese"]
    numOutputLangs = len(outputLangCodes)

class SpreadsheetTitleRow(Widget):
    _gridLayout = None

    def initialize(self, languageNames):
        for language in languageNames:
            label = Label(text=language, halign="center")
            self._gridLayout.add_widget(label, 2)  # Needs to be 2 from the end - before the thumbnail and delete columns

class Spreadsheet():
    def __init__(self):
        self.rows = []

    def get_input_words(self):
        inputWords = []
        for row in self.rows:
            inputWords.append(row.inputWord)
        return inputWords

    def build_dict(self):
        translationsDict = {}
        for row in self.rows:
            translatedWords = []
            for cell in row.outputWordCells:
                translatedWords.append(cell.text)
            translationsDict[row.inputWord] = translatedWords

        return translationsDict

class SpreadsheetRow(Widget):
    inputWord = StringProperty()
    imgFilepath = StringProperty()

    def __init__(self, **kwargs):
        self.gridLayout = None
        self.imgFilepath = kwargs.pop("imgFilepath")
        inputWord = kwargs.pop("inputWord")
        self.parentSheet = kwargs.pop("parentSheet")
        outputWordsList = kwargs.pop("outputWords")
        self.outputWordCells = []
        super().__init__(**kwargs)

        # For some reason this needs to go after the super init, or it doesn't appear
        self.inputWord = inputWord

        # Add this row into the parent spreadsheet
        if self.parentSheet is not None:
            self.parentSheet.rows.append(self)
        else:
            print("my parent sheet was none, weird")

        # Create input cells for each output language
        self.numOutputLangs = len(outputWordsList)
        for i in range (0, self.numOutputLangs):
            outputLangWidget = TextInput(text=outputWordsList[i], multiline=False)
            self.gridLayout.add_widget(outputLangWidget, 2) # Needs to be 2 from the end - before the thumbnail and delete columns
            self.outputWordCells.append(outputLangWidget)

    def delete_this_row(self, instance):
        Translator._instance.remove_spreadsheet_row(self)

class Thumbnail(Widget):
    _image = None
    filepath = StringProperty("")

    def __init__(self, **kwargs):
        self.name = StringProperty("")
        super().__init__(**kwargs)
        self.tryTime = 0
        Clock.schedule_interval(self.reload_img, 10)

    def reload_img(self, dt):
        self._image.reload()

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

class FilePickerPopup(Popup):
    _path = StringProperty(".")
    _filechooser = None
    _selectButton = None

    def __init__(self, **kwargs):
        self._path = kwargs.pop("path")
        self.onselect = kwargs.pop("onselect")
        super().__init__(**kwargs)

    def on_selected(self, filepath, filename):
        path = filepath
        if len(filename) > 0:
            path = join(filepath, filename[0])
        self.onselect(path)
        self.dismiss()

class SelectImportSpreadsheetPopup(FilePickerPopup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_selected(self, filepath, filename):
        Preferences.importSpreadsheetPath = filepath
        super().on_selected(filepath,filename)

class SelectExportFolderPopup(FilePickerPopup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._filechooser.dirselect = True
        self._filechooser.filters = [self.is_dir]
        self._selectButton.text = "Use this folder"

    def on_selected(self, filepath, filename):
        Preferences.exportSpreadsheetPath = filepath
        super().on_selected(filepath,filename)

    def is_dir(self, directory, filename):
        return isdir(join(directory, filename))

class Translator(Widget):
    _instance = None
    _spreadsheet = Spreadsheet()
    _spreadsheetViewer = None
    _spreadsheetTitleRow = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._spreadsheetTitleRow.initialize(Preferences.outputLangNames)
        self.create_empty_spreadsheet_row()

    # allow the user to bulk input food items to be translated
    def paste_input_words(self):
        popup = InputWordsPopup(title="One food item per line")
        popup.open()

    # overwrite all data with new images and translations
    def generate_translations(self):
        inputWords = self._spreadsheet.get_input_words()
        self.reset_spreadsheet()
        translationsDict = WordTranslator().generate_translations_dict(inputWords, Preferences.outputLangCodes)
        ImageDownloader().get_images_for_words(list(translationsDict.keys()))
        self.create_spreadsheet_rows_from_dict(translationsDict)

    # only fill in rows with missing translations, and generate missing images
    def generate_missing_translations(self):
        # Cache them off so we can delete them as we go
        spreadsheetRows = self._spreadsheet.rows
        for row in spreadsheetRows:
            # If the row has any empty words, retranslate it
            retranslate = False
            for cell in row.outputWordCells:
                if cell.text is "":
                    retranslate = True
            # If the row is missing an image filepath, we also need to retranslate it
            if row.imgFilepath is "":
                retranslate = True

            if retranslate:
                outputWordsList = WordTranslator().get_translated_words(row.inputWord, Preferences.outputLangCodes)
                i = 0
                for cell in row.outputWordCells:
                    cell.text = outputWordsList[i]
                    i += 1
                # See if an image exists but we just haven't loaded it
                row.imgFilepath = self.try_get_filepath_for_thumbnail(row.inputWord)
                # If it really doesn't exist, download a new one and then try to find it
                if row.imgFilepath is "":
                    ImageDownloader().get_images_for_words([row.inputWord])
                    row.imgFilepath = self.try_get_filepath_for_thumbnail(row.inputWord)

    # asks the user where to export to
    def export_to_spreadsheet(self):
        popup = SelectExportFolderPopup(
            title='Select output folder',
            path=Preferences.exportSpreadsheetPath,
            onselect=self.export_to_spreadsheet2)
        popup.open()

    # takes contents on screen and creates a spreadsheet
    def export_to_spreadsheet2(self, folder):
        outputFile = join(folder, "outputTranslations.xlsx")
        WordTranslator().write_dict_to_spreadsheet(self._spreadsheet.build_dict(), outputFile, Preferences.outputLangNames)

    # reads contents of spraedsheet and updates contents on screen
    def import_from_spreadsheet(self):
        popup = SelectImportSpreadsheetPopup(
            title='Select import spreadsheet',
            path=Preferences.importSpreadsheetPath,
            onselect=self.load_spreadsheet_from_file)
        popup.open()

    # loads in a spreadsheet
    def load_spreadsheet_from_file(self, filePathWithName):
        Translator._instance.create_spreadsheet_rows_from_dict(SpreadsheetWrangler.build_translations_dict(filePathWithName))

    # creates a new blank spreadsheet row
    def create_empty_spreadsheet_row(self):
        outputwords = []
        for _ in range (0, Preferences.numOutputLangs):
            outputwords.append("")
        self.create_spreadsheet_row("", outputwords, "")

    # creates a spreadsheet row, filled with given data
    def create_spreadsheet_row(self, inputWord, outputWords, imgFilePath):
        newRow = SpreadsheetRow(parentSheet=self._spreadsheet, inputWord=inputWord, outputWords=outputWords, imgFilepath=imgFilePath)
        self._spreadsheetViewer.add_widget(newRow)

    # removes the given row from our spreadsheet obj and the ui
    def remove_spreadsheet_row(self, row):
        self._spreadsheetViewer.remove_widget(row)
        self._spreadsheet.rows.remove(row)

    # creates the final images
    def output_images(self):
        FinalImageCreater().main("")

    # creates spreadsheet rows from a dict of translations, finding images if they exist
    def create_spreadsheet_rows_from_dict(self, translationsDict):
        self.reset_spreadsheet()
        for inputWord, outputWords in translationsDict.items():
            filepath = self.try_get_filepath_for_thumbnail(inputWord)

            # Add the row to the spreadsheet viewer
            newRow = SpreadsheetRow(parentSheet=self._spreadsheet, inputWord=inputWord, outputWords=outputWords, imgFilepath=filepath)
            self._spreadsheetViewer.add_widget(newRow)

    # try to find an image for the thumbnail - tries jpg and png. doesn't do anything with casing
    # if it can't find it, it returns empty string
    def try_get_filepath_for_thumbnail(self, word):
        # Try to come up with an appropriate image path
        filepath = "../foodThumbnails/" + word + ".jpg"
        if not Path(filepath).is_file():
            filepath = "../foodThumbnails/" + word + ".png"
            if not Path(filepath).is_file():
                print ("Could not find an appropriate thumbnail for " + word)
                filepath = ""

        return filepath

    # clears the spreadsheet out
    def reset_spreadsheet(self):
        self._spreadsheetViewer.clear_widgets()
        self._spreadsheet.rows = []

class MainApp(App):
    def build(self):
        Window.maximize()
        return Translator()

if __name__ == '__main__':
    MainApp().run()
