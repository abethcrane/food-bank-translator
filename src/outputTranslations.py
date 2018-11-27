import http.client, json, urllib.parse, uuid
from openpyxl import Workbook

class WordTranslator():

    subscriptionKey = open("../subscriptionKeys/translatorSubscriptionKey.txt").read()
    host = 'api.cognitive.microsofttranslator.com'
    path = '/translate?api-version=3.0'

    def main(self, inputWords, outputspreadsheet, outputLangs):
        print("I'll print each word when I finish translating it")

        dict = self.generate_translations_dict(inputWords, outputLangs)
        self.write_dict_to_spreadsheet(dict, outputspreadsheet)

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
        result = self.get_translations_from_server(inputWord, outputLangs)
        return self.get_words_from_result(result)

    def write_dict_to_spreadsheet(self, translationsDict, outputspreadsheet):
        # Initialize the spreadsheet
        workbook = Workbook(write_only=True)
        worksheet = workbook.create_sheet("translations")
        worksheet.append(["English", "Simplified Chinese", "Spanish", "Vietnamese"])

        # Append the list of words  to the spreadsheet
        for inputWord, outputWords in translationsDict.items():
            translatedWords = outputWords
            translatedWords.insert(0, inputWord)
            worksheet.append(translatedWords)

        workbook.save(outputspreadsheet)

    # gets server translation json for a given word to the given output langs
    def get_translations_from_server(self, word, outputLangs):
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

        conn = http.client.HTTPSConnection(self.host)
        conn.request ("POST", self.path + params, content, headers)
        response = conn.getresponse()
        return response.read()
    
    @staticmethod
    # converts output json into a list of the translated words
    def get_words_from_result(result):
        jsonData = json.loads(result)
        words = []
        for language in jsonData[0]["translations"]:
            words.append(language["text"])
            
        return words
        
if __name__ == '__main__':
    WordTranslator().main(list(open("../words.txt")), "../translatedWords.xlsx", list(open("../toLanguages.txt"))[1:])