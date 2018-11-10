import http.client, urllib.parse, uuid, json
from openpyxl import Workbook

subscriptionKey =  open("translatorSubscriptionKey.txt").read()

host = 'api.cognitive.microsofttranslator.com'
path = '/translate?api-version=3.0'

def getTranslationsFromServer (word):
    requestBody = [{
        'Text' : word,
    }]

    headers = {
        'Ocp-Apim-Subscription-Key': subscriptionKey,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    content = json.dumps(requestBody, ensure_ascii=False).encode('utf-8')

    conn = http.client.HTTPSConnection(host)
    conn.request ("POST", path + params, content, headers)
    response = conn.getresponse()
    return response.read()
    
def getWordsFromResult(result):
    jsonData = json.loads(result)
    words = []
    for language in jsonData[0]["translations"]:
        words.append(language["text"])
        
    return words

print("I'll print each word when I finish translating it")

# Initialize the spreadsheet
workbook = Workbook(write_only=True)
worksheet = workbook.create_sheet("translations")
worksheet.append(["English", "Simplified Chinese", "Spanish", "Vietnamese"])

# Open input file and combine the languages we're translating to into a params string
params = "";
toLanguages = list(open("toLanguages.txt"))
for lang in toLanguages[1:]:
    params += "&to=" + lang.lstrip().rstrip()

# Read in all the words and translate them
wordsToTranslate = list(open("words.txt"))
for word in wordsToTranslate:
    word = word.lstrip().rstrip().capitalize()
    result = getTranslationsFromServer(word)
    translatedWords = getWordsFromResult(result)
    
    # Append the list of words  to the spreadsheet
    translatedWords.insert(0, word)
    worksheet.append(translatedWords)

    print(word)

workbook.save("translatedWords.xlsx")