import glob
import numpy
import imageio

from pyforms.basewidget import BaseWidget
from pyforms.controls   import ControlButton
from pyforms.controls   import ControlFile
from pyforms.controls   import ControlImage
from pyforms.controls   import ControlList
from pyforms.controls   import ControlText
from pyforms.controls   import ControlTextArea

from outputTranslations import WordTranslator
from outputImages import FinalImageCreater
from findAndSaveImages import ImageDownloader

class TranslatorApp(BaseWidget):

    def __init__(self, *args, **kwargs):
        super().__init__('Foodbank Translator App')

        #Definition of the forms fields
        self._inputWords    = ControlTextArea('InputWords')
        self._outputfile    = ControlText('Results output file')
        self._outputTranslationsButton     = ControlButton('Output Translations')
        self._spreadsheetLocation     = ControlFile('Translated Words Spreadsheet')
        self.downloadThumbnailsButton     = ControlButton('Find Thumbnails')
        self.outputImagesButton     = ControlButton('Output Images')
        self.thumbnails0     = ControlImage('DownloadedThumbnails')
        self.thumbnails1     = ControlImage('DownloadedThumbnails')
        self.thumbnails2     = ControlImage('DownloadedThumbnails')
        self.thumbnails3     = ControlImage('DownloadedThumbnails')
        self.thumbnails4     = ControlImage('DownloadedThumbnails')
        self.thumbnails5     = ControlImage('DownloadedThumbnails')
        self.thumbnails6     = ControlImage('DownloadedThumbnails')
        #Define the event that will be called when the run button is processed
        self._outputTranslationsButton.value       = self.__outputTranslations
        self.downloadThumbnailsButton.value       = self._downloadThumbnails
        self.outputImagesButton.value       = self._createImages

        #Define the organization of the Form Controls
        self._formset = [
            ('_outputfile', '_outputTranslationsButton', 'downloadThumbnailsButton'),
            '_inputWords',
            ('thumbnails0', 'thumbnails1', 'thumbnails2', 'thumbnails3', 'thumbnails4', 'thumbnails5', 'thumbnails6' ),
            ('_spreadsheetLocation', 'outputImagesButton')
        ]

    def __outputTranslations(self):
        words = self._inputWords.value.split("\n")
        WordTranslator().main(words)

    def _downloadThumbnails(self):
        spreadsheet = self._spreadsheetLocation.value
        FinalImageCreater().main(spreadsheet)
        list = []
        for filepath in glob.iglob("foodThumbnails/*"):
            image = imageio.imread(filepath)
            list.append(image)
        self.thumbnails0.value = list[0]
        self.thumbnails1.value = list[1]
        self.thumbnails2.value = list[2]
        self.thumbnails3.value = list[3]
        self.thumbnails4.value = list[4]
        self.thumbnails5.value = list[5]
        self.thumbnails6.value = list[6]

    def _createImages(self):
        spreadsheet = self._spreadsheetLocation.value
        FinalImageCreater().main(spreadsheet)
                        
if __name__ == '__main__':
    from pyforms import start_app
    start_app(TranslatorApp)

    