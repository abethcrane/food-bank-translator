import os, sys, shutil, unittest
from spreadsheetWrangler import SpreadsheetWrangler
from fontManipulator import FontManipulator
from wordTranslator import WordTranslator
from finalImageCreator import FinalImageCreator

thismodule = sys.modules[__name__]
thismodule.fontLocation = "NotoSansCJKsc-Light.otf"
thismodule.spreadsheetName = "testTranslatedWords.xlsx"
thismodule.outputImagesFolder = "testimages"

class TestFontManipulator(unittest.TestCase):
    def test_find_font_size_to_fit_height(self):
        self.assertEqual(195, FontManipulator.find_font_size_to_fit_height(['Flour', '面粉', 'Harina', 'Bột'], 1754, thismodule.fontLocation, 200, 100))
        self.assertEqual(200, FontManipulator.find_font_size_to_fit_height(['Salt', '盐', 'Sal', 'Muối'], 1754, thismodule.fontLocation, 200, 100))
        
    def test_find_font_size_to_fit_width(self):
        self.assertEqual(171, FontManipulator.find_font_size_to_fit_width("Copos de pimiento rojo", 1818, thismodule.fontLocation, 200))
        self.assertEqual(200, FontManipulator.find_font_size_to_fit_width("Chicken broth", 1818, thismodule.fontLocation, 200))

class TestMain(unittest.TestCase):
    # the order of these is important - they depend upon each other
    # should that be the case? perhaps not!

    def test_wordTranslator_does_not_throw(self):
        WordTranslator().main(
        ["fish", "apples"],
        thismodule.spreadsheetName,
        ["zh-Hans", "es", "vi"],
        ["Simplified Chinese", "Spanish", "Vietnamese"])

    def test_finalImageCreator_does_not_throw(self):
        # doesn't throw even if the folder hasn't been created
        FinalImageCreator().main(
        thismodule.spreadsheetName,
        thismodule.outputImagesFolder)

    #TODO test if given invalid spreadsheet location

    def magic_test_cleanup(self):
        os.remove(thismodule.spreadsheetName)
        shutil.rmtree(thismodule.outputImagesFolder, ignore_errors=True)

        self.assertFalse(os.path.exists(thismodule.spreadsheetName))
        self.assertFalse(os.path.exists(thismodule.outputImagesFolder))

if __name__ == '__main__':
    unittest.main()