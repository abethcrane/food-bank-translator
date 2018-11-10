from pyforms.basewidget import BaseWidget
from pyforms.controls   import ControlButton
from pyforms.controls   import ControlText
from pyforms.controls   import ControlTextArea
from pyforms.controls   import ControlFile

from outputTranslations import WordTranslator
from outputImages import FinalImageCreater

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

        #Define the event that will be called when the run button is processed
        self._outputTranslationsButton.value       = self.__outputTranslations
        #self.downloadThumbnailsButton.value       = self.__runEvent
        self.outputImagesButton.value       = self._createImages

        #Define the organization of the Form Controls
        self._formset = [
            ('_outputfile', '_outputTranslationsButton'),
            '_inputWords',
            ('_spreadsheetLocation', 'outputImagesButton')
        ]

    def __outputTranslations(self):
        words = self._inputWords.value.split("\n")
        WordTranslator().main(words)

    def _createImages(self):
        spreadsheet = self._spreadsheetLocation.value
        FinalImageCreater().main(spreadsheet)
                        
if __name__ == '__main__':
    from pyforms import start_app
    start_app(TranslatorApp)