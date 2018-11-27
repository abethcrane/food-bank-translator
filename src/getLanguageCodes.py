import http.client, json, sys, urllib.parse

thismodule = sys.modules[__name__]

thismodule.subscriptionKey =  open("subscriptionKey.txt").read()
thismodule.host = 'api.cognitive.microsofttranslator.com'
thismodule.path = '/languages?api-version=3.0'
thismodule.outputPath = 'languageCodes.txt'

def get_available_languages():
    headers = {'Ocp-Apim-Subscription-Key': thismodule.subscriptionKey}

    conn = http.client.HTTPSConnection(thismodule.host)
    conn.request ("GET", thismodule.path, None, headers)
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

f = open(thismodule.outputPath, 'w')
f.write(niceResults)  
f.close
