import http.client, json, os, sys, urllib.parse, uuid
from os.path import join
from socket import gaierror
from spreadsheetWrangler import SpreadsheetWrangler

thismodule = sys.modules[__name__]
thismodule.scriptdir = os.path.dirname(os.path.realpath(__file__))
thismodule.parentdir = join(thismodule.scriptdir, "..")

class WordTranslator():
    def __init__(self):
        subscriptionKeysFolder = join(thismodule.parentdir, "subscriptionKeys")
        subscriptionKeyPath = join(subscriptionKeysFolder, "translatorSubscriptionKey.txt")
        self.subscriptionKey = open(subscriptionKeyPath).read()
        self.host = 'api.cognitive.microsofttranslator.com'
        self.path = '/translate?api-version=3.0'

    def translate_words_and_create_spreadsheet(self, inputWords, outputspreadsheet, outputLangCodes, outputLangNames):
        print("I'll print each word when I finish translating it")

        translationsDict = self.generate_translations_dict(inputWords, outputLangCodes)
        SpreadsheetWrangler.write_dict_to_spreadsheet(translationsDict, outputspreadsheet, outputLangCodes)

        print ("I'm finished translating words")
        
    # returns a dict like {fish: [鱼, Pescado, Cá], kidney beans: [芸豆, Frijoles, Đậu thận]}
    def generate_translations_dict(self, inputWords, outputLangs):
        translations = {}

        for word in inputWords:
            word = word.lstrip().rstrip().capitalize()

            # Empty words get an empty response
            if word is None or word is "":
                translatedWords = []
                for _ in outputLangs:
                    translatedWords.append("")
            else:
                translatedWords = self.get_translated_words(word, outputLangs)

            translations[word] = translatedWords
            print(word)

        return translations

    def get_translated_words(self, inputWord, outputLangs):
        result = self.__get_translations_from_server(inputWord, outputLangs)
        return self.__get_words_from_result(result)

    # gets server translation json for a given word to the given output langs
    def __get_translations_from_server(self, word, outputLangs):
        params = ""
        for lang in outputLangs:
            params += "&to=" + lang.lstrip().rstrip()

        requestBody = [{
            'Text' : word,
        }]

        headers = {
            'Ocp-Apim-Subscription-Key': self.subscriptionKey,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }

        content = json.dumps(requestBody, ensure_ascii=False).encode('utf-8')
        try:
            conn = http.client.HTTPSConnection(self.host)
            conn.request ("POST", self.path + params, content, headers)
            response = conn.getresponse()
            return response.read()
        except gaierror:
            return None
    
    @staticmethod
    # converts output json into a list of the translated words
    def __get_words_from_result(result):
        if result == None:
            return []

        jsonData = json.loads(result)
        words = []
		
        for language in jsonData[0]["translations"]:
            words.append(language["text"])
            
        return words
        
if __name__ == '__main__':
    inputFolder = join(thismodule.parentdir, "input")
    outputFolder = join(thismodule.parentdir, "output")
    WordTranslator().translate_words_and_create_spreadsheet(
        list(open(join(inputFolder, "words.txt"))),
        join(outputFolder,"translatedWords.xlsx"),
        list(open(join(inputFolder, "toLanguages.txt")))[1:],
        ["Simplified Chinese", "Spanish", "Vietnamese"]) # Yeah it's a bit of a hardcoded cheat, I know