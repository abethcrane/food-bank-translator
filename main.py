import glob
import io
from pathlib import Path

from kivy.app import App
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
from outputImages import FinalImageCreater
from findAndSaveImages import ImageDownloader

class Thumbnail(Widget):
    filepath = ""
    image = None
    label = None
    name = StringProperty("")

    def calculateSize(self):
        if not self.image or not self.image.texture:
            return self.size
        return ((self.label.size[0] + self.image.texture.size[0]) * 2, (self.label.size[1] + self.image.texture.size[1]) * 2) #(self.image.norm_image_size[0] * 2, self.image.norm_image_size[1] * 2)

    calculatedSize = AliasProperty(calculateSize, None)
    def calculatePos(self):
        return self.center_x - self.calculatedSize[0] / 2, self.center_y - self.calculatedSize[1] / 2
    calculatedPos = AliasProperty(calculatePos, None)

    def __init__(self, **kwargs):
        self.filepath = kwargs.pop('filepath')
        print (self.filepath)
        super().__init__(**kwargs)

        fbind = self.fbind
        fbind('filepath', self.update)
        if self.filepath is not "":
            self.update()

    def update(self):
        self.name = Path(self.filepath).stem
        self.calculateSize()
        self.calculatePos()
        print(self.calculatedSize)


class ImageViewer(Widget):    
    gridLayout = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clear_widgets()

        gridLayout = GridLayout(cols = 1)
        self.add_widget(gridLayout)

        button1 = Button(text = "Download Thumbnails")
        button1.bind(on_press=self.DownloadThumbnails)
        gridLayout.add_widget(button1)

        for thumbnail in self.thumbnails:
            gridLayout.add_widget(thumbnail)

    def DisplayThumbnails(self):
        self.clear_widgets()

        ImageDownloader().main("")
        for filepath in glob.iglob("foodThumbnails/*"):
            thumb = Image(source=filepath)
            self.gridLayout.add_widget(thumb)

class Translator(Widget):

    imageViewer = None 
    inputWords = TextInput()

    lang1 = StringProperty("Hello")
    lang2 = StringProperty("World")
    lang3 = StringProperty("This is me")

    def DisplayThumbnails(self):
        self.imageViewer.clear_widgets()

        #ImageDownloader().main("")
        for filepath in glob.iglob("foodThumbnails/*"):
            thumb = Thumbnail(filepath=filepath)
            self.imageViewer.add_widget(thumb)

    def OutputTranslations(self, inputWords):
        translations = WordTranslator().main(inputWords.text.split("\n"))
        self.lang1 = "\n".join(translations[0])
        self.lang2 = "\n".join(translations[1])
        self.lang3 = "\n".join(translations[2])
        print (self.lang1 + self.lang2)


class MainApp(App):
    def build(self):
        layout = GridLayout(cols=3)
        layout.add_widget(Translator())

        return layout

if __name__ == '__main__':
    MainApp().run()