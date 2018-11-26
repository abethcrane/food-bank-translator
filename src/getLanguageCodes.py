import http.client, urllib.parse, json

subscriptionKey =  open("subscriptionKey.txt").read()

host = 'api.cognitive.microsofttranslator.com'
path = '/languages?api-version=3.0'

output_path = 'languageCodes.txt'

def get_available_languages():
    headers = {'Ocp-Apim-Subscription-Key': subscriptionKey}

    conn = http.client.HTTPSConnection(host)
    conn.request ("GET", path, None, headers)
    response = conn.getresponse()
    return response.read()
    
def cleanup_results(results):
    jsondata = json.loads(result)
    printLines = []
    for languageCode in jsondata["translation"]:
        languageName = jsondata["translation"][languageCode]["name"]
        printLines.append(languageName + ": " + languageCode)
    
    return "\n".join(printLines)

result = get_available_languages()
niceResults = cleanup_results(result)

f = open(output_path, 'w')
f.write(niceResults)  
f.close
