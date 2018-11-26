import http.client, json, urllib.parse, uuid
from openpyxl import Workbook

class WordTranslator():

    subscriptionKey = open("../subscriptionKeys/translatorSubscriptionKey.txt").read()
    host = 'api.cognitive.microsofttranslator.com'
    path = '/translate?api-version=3.0'

    def main(self, inputWords):
        print("I'll print each word when I finish translating it")

        # Read in all the words and translate them
        if len(inputWords) is 0:
            wordsToTranslate = list(open("../words.txt"))
        else:
            wordsToTranslate = inputWords

        dict = self.generate_translations_dict(wordsToTranslate)
        self.write_dict_to_spreadsheet(dict)

        print ("I'm finished translating words")
        
    def generate_translations_dict(self, inputWords):
        # Open input file and combine the languages we're translating to into a params string
        params = ""
        toLanguages = list(open("../toLanguages.txt"))
        for lang in toLanguages[1:]:
            params += "&to=" + lang.lstrip().rstrip()

        translations = {}

        for word in inputWords:
            word = word.lstrip().rstrip().capitalize()

            # Empty words get an empty response
            if word is None or word is "":
                translatedWords = []
                for lang in toLanguages[1:]:
                    translatedWords.append("")
            else:
                result = self.get_translations_from_server(params, word)
                translatedWords = self.get_words_from_result(result)

            translations[word] = translatedWords

            print(word)

        return translations

    def write_dict_to_spreadsheet(self, translationsDict):
        # Initialize the spreadsheet
        workbook = Workbook(write_only=True)
        worksheet = workbook.create_sheet("translations")
        worksheet.append(["English", "Simplified Chinese", "Spanish", "Vietnamese"])

        # Append the list of words  to the spreadsheet
        for inputWord, outputWords in translationsDict.items():
            translatedWords = outputWords
            translatedWords.insert(0, inputWord)
            worksheet.append(translatedWords)

        workbook.save("../translatedWords.xlsx")

    def get_translations_from_server (self, params, word):
        requestBody = [{
            'Text' : word,
        }]

        headers = {
            'Ocp-Apim-Subscription-Key': self.subscriptionKey,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }

        content = json.dumps(requestBody, ensure_ascii=False).encode('utf-8')

        conn = http.client.HTTPSConnection(self.host)
        conn.request ("POST", self.path + params, content, headers)
        response = conn.getresponse()
        return response.read()
    
    @staticmethod
    def get_words_from_result(result):
        jsonData = json.loads(result)
        words = []
        for language in jsonData[0]["translations"]:
            words.append(language["text"])
            
        return words

if __name__ == '__main__':
    WordTranslator().main([])