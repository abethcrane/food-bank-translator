from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import AliasProperty, StringProperty
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

class Thumbnail(Widget):
    image = None
    label = None
    name = StringProperty("")
    filepath = StringProperty("")
    tryTime = 0

    def __init__(self, **kwargs):
        super(Thumbnail,self).__init__(**kwargs)
        Clock.schedule_interval(self.reloadImg, 10)

    def reloadImg(self, dt):
        self.image.reload()

    def DownloadNewThumb(self):
        (img, self.tryTime) = ImageDownloader().getNextImage(self.name, self.tryTime +1)
        ImageDownloader.thumbifyAndSave(self.name, img)
        self.reloadImg(1)

class Translator(Widget):

    imageViewer = None 
    inputWords = None

    lang1 = StringProperty("")
    lang2 = StringProperty("")
    lang3 = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        wordLists = SpreadsheetWrangler.getListsOfWordsPerLanguage("../translatedWords.xlsx")
        self.inputWords.text = "\n".join(wordLists[0])
        self.lang1 = "\n".join(wordLists[1])
        self.lang2 = "\n".join(wordLists[2])
        self.lang3 = "\n".join(wordLists[3])

    def DisplayThumbnails(self):
        self.imageViewer.data = []

        englishWords = SpreadsheetWrangler.getListsOfWordsPerLanguage("../translatedWords.xlsx")[0]
        for word in englishWords:
            filepath = "../foodThumbnails/" + word + ".jpg"
            if Path(filepath).is_file():
                self.imageViewer.data.append({'filepath': filepath, 'name': word})
            else:
                filepath = "../foodThumbnails/" + word + ".png"
                if Path(filepath).is_file():
                    self.imageViewer.data.append({'filepath': filepath, 'name': word})

    def OutputImages(self):
        FinalImageCreater().main("")

    def OutputTranslations(self, inputWords):
        translations = WordTranslator().main(self.inputWords.text.split("\n"))
        self.lang1 = "\n".join(translations[0])
        self.lang2 = "\n".join(translations[1])
        self.lang3 = "\n".join(translations[2])

        ImageDownloader().main("")


class MainApp(App):
    def build(self):
        layout = GridLayout(cols=3)
        layout.add_widget(Translator())
        return layout

if __name__ == '__main__':
    MainApp().run()