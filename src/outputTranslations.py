import http.client, urllib.parse, uuid, json
from openpyxl import Workbook

class WordTranslator():

    subscriptionKey = ""
    host = 'api.cognitive.microsofttranslator.com'
    path = '/translate?api-version=3.0'

    def main(self, inputWords):
        self.subscriptionKey = open("../subscriptionKeys/translatorSubscriptionKey.txt").read()
    
        print("I'll print each word when I finish translating it")

        # Initialize the spreadsheet
        workbook = Workbook(write_only=True)
        worksheet = workbook.create_sheet("translations")
        worksheet.append(["English", "Simplified Chinese", "Spanish", "Vietnamese"])

        # Open input file and combine the languages we're translating to into a params string
        params = "";
        toLanguages = list(open("../toLanguages.txt"))
        for lang in toLanguages[1:]:
            params += "&to=" + lang.lstrip().rstrip()

        # Read in all the words and translate them
        if len(inputWords) is 0:
            wordsToTranslate = list(open("../words.txt"))
        else:
            wordsToTranslate = inputWords

        translations = [[], [], []]

        for word in wordsToTranslate:
            word = word.lstrip().rstrip().capitalize()
            result = self.getTranslationsFromServer(params, word)
            translatedWords = self.getWordsFromResult(result)
            
            # Append the list of words  to the spreadsheet
            translatedWords.insert(0, word)
            worksheet.append(translatedWords)

            translations[0].append(translatedWords[1])
            translations[1].append(translatedWords[2])
            translations[2].append(translatedWords[3])

            print(word)

        workbook.save("../translatedWords.xlsx")

        return translations
        
    def getTranslationsFromServer (self, params, word):
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
    def getWordsFromResult(result):
        jsonData = json.loads(result)
        words = []
        for language in jsonData[0]["translations"]:
            words.append(language["text"])
            
        return words

if __name__ == '__main__':
    WordTranslator().main("")