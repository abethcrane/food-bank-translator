import glob
import io
import os

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.slider import Slider
from kivy.uix.widget import Widget
from kivy.uix.recycleview import RecycleView

from outputTranslations import WordTranslator
from outputImages import FinalImageCreater
from findAndSaveImages import ImageDownloader

class Thumbnail(Widget):
    name = ""
    image = None
    source = ""
        
    def init(self, filepath):
        self.name = os.path.basename(filepath)
        self.image.source = filepath

class ImageViewer(Widget):
    pass

class Translator(Widget):

    imageViewer = None
    lang1 = ""
    lang2 = ""
    lang3 = ""

    def build(self):
        pass

    def OutputTranslations(self, inputWords):
        WordTranslator().main(inputWords.text.split("\n"))

    def DownloadThumbnails(self):
        self.imageViewer.clear_widgets()
        translations = ImageDownloader().main("")
        self.lang1 = "\n".join(translations[0])
        self.lang2 = "\n".join(translations[1])
        self.lang3 = "\n".join(translations[2])

        print(self.lang1 + self.lang2 + self.lang3)
        for filepath in glob.iglob("foodThumbnails/*"):
            self.imageViewer.add_widget(Image(source=filepath))

class MainApp(App):
    def build(self):
        return Translator()

if __name__ == '__main__':
    MainApp().run()