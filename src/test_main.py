import os, pytest, sys, shutil
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

class TestFontManipulator(object):
    def test_find_font_size_to_fit_height(self):
        assert (195 == FontManipulator.find_font_size_to_fit_height(['Flour', '面粉', 'Harina', 'Bột'], 1754, thismodule.fontLocation, 200, 100))
        assert (200 == FontManipulator.find_font_size_to_fit_height(['Salt', '盐', 'Sal', 'Muối'], 1754, thismodule.fontLocation, 200, 100))
        
    def test_find_font_size_to_fit_width(self):
        assert (171 == FontManipulator.find_font_size_to_fit_width("Copos de pimiento rojo", 1818, thismodule.fontLocation, 200))
        assert (200 == FontManipulator.find_font_size_to_fit_width("Chicken broth", 1818, thismodule.fontLocation, 200))

class TestCrashes(object):
    # the order of these is important - they depend upon each other
    # should that be the case? perhaps not!

    def test_wordTranslator_does_not_throw(self):
        WordTranslator().main(
        ["fish", "apples"],
        thismodule.spreadsheetName,
        ["zh-Hans", "es", "vi"],
        ["Simplified Chinese", "Spanish", "Vietnamese"])

    def test_finalImageCreator_does_not_throw(self):
        print (thismodule.fontLocation)

        # doesn't throw even if the folder hasn't been created
        FinalImageCreator().main(
        thismodule.spreadsheetName,
        thismodule.outputImagesFolder,
        join(join(thismodule.parentdir, "output"), "foodThumbnails"))

    #TODO test if given invalid spreadsheet location

    def magic_test_cleanup(self):
        os.remove(thismodule.spreadsheetName)
        shutil.rmtree(thismodule.outputImagesFolder, ignore_errors=True)

        assert (False == os.path.exists(thismodule.spreadsheetName))
        assert (False == os.path.exists(thismodule.outputImagesFolder))