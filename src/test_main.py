import inspect, os, pytest, sys, shutil
from os.path import join

from spreadsheetWrangler import SpreadsheetWrangler
from fontManipulator import FontManipulator
from wordTranslator import WordTranslator
from finalImageCreator import FinalImageCreator

thismodule = sys.modules[__name__]
thismodule.scriptdir = os.path.dirname(os.path.realpath(__file__))
thismodule.parentdir = join(thismodule.scriptdir, "..")
thismodule.fontLocation = join(thismodule.scriptdir, "NotoSansCJKsc-Light.otf")
thismodule.spreadsheetName = join(join(thismodule.parentdir, "tests"), "testTranslatedWords.xlsx")
thismodule.outputImagesFolder = join(join(thismodule.parentdir, "tests"), "testimages")

class WordTranslatorStub():
    def no_init(self):
        pass

    def stubbed_word_translator(self, inputWords, outputspreadsheet, outputLangCodes, outputLangNames):
        # We ignore the input words and the desired languages
        translationsDict = {"fish": ["鱼", "Pescado", "Cá"], "kidney beans": ["芸豆", "Frijoles", "Đậu thận"]}
        SpreadsheetWrangler.write_dict_to_spreadsheet(translationsDict, outputspreadsheet, outputLangCodes)

class TestFontManipulator(object):
    def test_find_font_size_to_fit_height(self):
        assert (195 == FontManipulator.find_font_size_to_fit_height(['Flour', '面粉', 'Harina', 'Bột'], 1754, thismodule.fontLocation, 200, 100))
        assert (200 == FontManipulator.find_font_size_to_fit_height(['Salt', '盐', 'Sal', 'Muối'], 1754, thismodule.fontLocation, 200, 100))
        
    def test_find_font_size_to_fit_width(self):
        assert (171 == FontManipulator.find_font_size_to_fit_width("Copos de pimiento rojo", 1818, thismodule.fontLocation, 200))
        assert (200 == FontManipulator.find_font_size_to_fit_width("Chicken broth", 1818, thismodule.fontLocation, 200))

class TestCrashes(object):
    # the order of these is important - they depend upon each other
    # should that be the case? probably not!

    def test_wordTranslator_stub_signature_matches(self):
        original = inspect.signature(WordTranslator.translate_words_and_create_spreadsheet)
        stub = inspect.signature(WordTranslatorStub.stubbed_word_translator)
        assert (original == stub)

    def test_wordTranslator_does_not_throw(self):
        # Use our stubbed word translator that doesn't require a subscription key
        WordTranslator.__init__ = WordTranslatorStub.no_init
        WordTranslator.translate_words_and_create_spreadsheet = WordTranslatorStub.stubbed_word_translator

        WordTranslator().translate_words_and_create_spreadsheet(
        ["fish", "apples"],
        thismodule.spreadsheetName,
        ["zh-Hans", "es", "vi"],
        ["Simplified Chinese", "Spanish", "Vietnamese"])

    def test_finalImageCreator_does_not_throw(self):
        # doesn't throw even if the folder hasn't been created
        FinalImageCreator().create_images(
        thismodule.spreadsheetName,
        thismodule.outputImagesFolder,
        join(join(thismodule.parentdir, "output"), "foodThumbnails"))

    #TODO test if given invalid spreadsheet location

    def magic_test_cleanup(self):
        os.remove(thismodule.spreadsheetName)
        shutil.rmtree(thismodule.outputImagesFolder, ignore_errors=True)

        assert (False == os.path.exists(thismodule.spreadsheetName))
        assert (False == os.path.exists(thismodule.outputImagesFolder))