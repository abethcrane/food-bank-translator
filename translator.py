import http.client, urllib.parse, uuid, json
from PIL import Image, ImageDraw, ImageFont

subscriptionKey =  open("subscriptionKey.txt").read()

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
    response = conn.getresponse ()
    return response.read ()
    
def getWordsFromResult(result):
    jsonData = json.loads(result)
    words = []
    for language in jsonData[0]["translations"]:
        words.append(language["text"])
        
    return words

# Open input file and combine the languages we're translating to into a params string
params = "";
toLanguages = list(open("toLanguages.txt"))
for lang in toLanguages[1:]:
    params += "&to=" + lang.lstrip().rstrip()
    
# Our font for the images
fnt = ImageFont.truetype('/Library/Fonts/Arial Unicode.ttf', 100)

# Read in all the words and translate them
wordsToTranslate = list(open("words.txt"))
for word in wordsToTranslate:
    word = word.lstrip().rstrip().capitalize()
    print(word)
    result = getTranslationsFromServer(word)
    translatedWords = getWordsFromResult(result)

    # Draw out the white background + the word we translated
    img = Image.new('RGB', (1024, 720), color = 'white')
    d = ImageDraw.Draw(img)
    height = 10
    d.text((10,height), word, font=fnt, fill=(0, 0, 0))
    height += 200
    
    # Print all the words onto the slide
    for translatedWord in translatedWords:
        d.text((10,height), translatedWord, font=fnt, fill=(0, 0, 0))
        height += 100
        
    # Save off the image
    img.save("images/" + word + '.png')
