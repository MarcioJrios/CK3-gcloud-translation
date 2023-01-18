from array import array
from numpy import array_split
import glob
import re
import sys
import math

# Imports the Google Cloud Translation library
from google.cloud import translate

linesPerFile = 150
# Initialize Translation client
def translate_text(texts, project_id="YOUR_PROJECT_ID"):
    """Translating Text."""

    client = translate.TranslationServiceClient()

    location = "global"

    parent = f"projects/{project_id}/locations/{location}"

    response = None
    response = client.translate_text(
        request={
            "parent": parent,
            "contents": texts,
            "mime_type": "text/plain",  # mime types: text/plain, text/html
            "source_language_code": "en",
            "target_language_code": "pt",
        }
    )

    # for translation in response.translations:
    #     print("Translated text: {}".format(translation.translated_text))
    return response.translations

def replace_text_in_file(originalTexts: array, translatedTexts: array, data: array, filePath: str):
    index = 0
    fileN = 0
    indexPart = 0
    for text in originalTexts:
        if (text[0] == ' '):
            text= text[1:len(text)+1]
        if (len(text) > 0 and text[len(text)-1] == ' '):
            text= text[0:len(text)-1]
        text = text.replace('...', '.')
        # pattern para substituir o texto entre aspas
        testPattern = re.compile(rf'(?m)((\b|\\n){re.escape(text)}(\b|\\n))(?=[^"]*"(?:[^"\r\n]*"[^"]*")*[^"\r\n]*$)')
        textTranslated = ''
        if (isinstance(translatedTexts[index], str)):
            textTranslated = translatedTexts[index]
        else:
            textTranslated = translatedTexts[index].translated_text

        found = False
        fakeData = data
        while fileN < len(fakeData):
            while indexPart < len(fakeData[fileN]): # textLine in enumerate(fakeData[fileN], start=indexPart):
                if re.search(testPattern, fakeData[fileN][indexPart]) is None:
                    print(text)
                    indexPart = indexPart + 1
                    continue
                else:
                    data[fileN][indexPart] = re.sub(testPattern, str.format(textTranslated), fakeData[fileN][indexPart], 1)
                    found = True
                    break
            if found == False:
                fileN = fileN + 1
                indexPart = 0
            else:
                break

        if fileN == len(data):
            fileN = 0
        index = index + 1
    textToWrite = ''
    for filePart in data:
        for fileLine in filePart:
            textToWrite = textToWrite + fileLine
    with open(rf'{filePath}', 'w', encoding="utf-8-sig") as file:
        # Writing the replaced data in our text file
        file.write(textToWrite)
        file.close()

def remove_hash(match: str):
    noHashList = []
    if '#' in match:
        # pattern = r'\b[^\#^\[^\]]*(?![^\#]*\]\#)\b'
        pattern = r'(?<=\#).+?(?=\#)'
        matches = re.split(pattern, match, re.MULTILINE)
        for newMatch in matches:
            len(newMatch) > 0 and newMatch != ' ' and newMatch != 'n' and newMatch != '\\' and newMatch != '(' and newMatch != ')' and noHashList.append(newMatch.replace('#', ''))
    else:
        noHashList.append(match)
    
    return noHashList

def remove_bracket(match: str):
    noHashList = []
    if '[' in match and ']' in match:
        pattern = r'[^\[^\]]*(?![^\[]*\])\b'
        texts = re.findall(pattern, match)
        for text in texts:
            len(text) > 0 and text != ' ' and text != 'n' and text != '\\' and text != '(' and text != ')' and noHashList.append(text)
    else:
        noHashList.append(match)
    
    return noHashList

def remove_amp(match: str):
    noHashList = []
    if '$' in match:
        pattern = r'(?=\$).+?\$'
        matches = re.split(pattern, match, re.MULTILINE)
        for newMatch in matches:
            len(newMatch) > 0 and newMatch != ' ' and newMatch != 'n' and newMatch != '\\' and newMatch != '(' and newMatch != ')' and noHashList.append(newMatch)
    else:
        noHashList.append(match)
    
    return noHashList

def remove_breakline(match: str):
    noBreakLineList = []
    if '\\n' in match:
        matches = match.split('\\n')
        for newMatch in matches:
            len(newMatch) > 0 and newMatch != ' ' and newMatch != 'n' and newMatch != '\\' and newMatch != '(' and newMatch != ')' and noBreakLineList.append(newMatch)
    else:
        noBreakLineList.append(match)
    
    return noBreakLineList

def remove_reticence(match: str):
    noReticenceList = []
    if '...' in match:
        matches = match.split('...')
        for newMatch in matches:
            len(newMatch) > 0 and newMatch != ' ' and newMatch != 'n' and newMatch != '\\' and newMatch != '(' and newMatch != ')' and noReticenceList.append(newMatch)
    else:
        noReticenceList.append(match)
    
    return noReticenceList

def translate_file(filePath):
    data = [[]] # array de dados/conteudo dos arquivos de tradução
    part = -1 # variavel auxiliar da parte atual do array de dados
    splitN = 1 # indica se o arquivo é muito grande e precisa ser dividido em partes

    # Abre o arquivo passado por parametro
    with open(rf'{filePath}', "r", encoding="utf-8-sig") as bigfile:
        fileSize = len(bigfile.read())
        splitN = math.ceil(fileSize / 30000)
        bigfile.seek(0)
        for lineno, line in enumerate(bigfile):
            if lineno % linesPerFile == 0:
                part = part + 1
                data.append([])
            data[part].append(line)

    # TODO performatizar o uso desses arrays
    matches1 = []
    matches2 = []
    matches3 = []
    matches4 = []
    matches5 = []
    originalText = []

    pattern = r'(?<=(["\'])).*?(?=\1)' # primeiro pattern para buscar o texto entre aspas
    # patterns = [r'(?<=(["\'])).*?(?=\1)', r'(?<=\#).+?(?=\#)', r'\b[^\[^\]]*(?![^\[]*\])\b', r'(?<=\$).+?(?=\$)']

    for filePart in data:
        for fileLine in filePart:
            matches1.extend(re.finditer(pattern, fileLine, re.MULTILINE))
    
    for matchNum, match in enumerate(matches1, start=1):
        text = match.group()
        len(text) > 0 and matches2.extend(remove_bracket(text))

    for match in matches2:
        matches3.extend(remove_amp(match))

    for match in matches3:
        matches4.extend(remove_breakline(match))
    
    for match in matches4:
        matches5.extend(remove_reticence(match))   

    for text in matches5:
        if len(text) > 0:
            text = removeEndWord(text)
            text = removeBackWord(text)
            if (len(text) > 0 and text[0] == ' '):
                text = text[1:len(text)] 
            if (text not in [' ', '\n', '']):
                originalText.append(text)

    translatedTexts = []

    if len(originalText) > 0:
        if (splitN > 1):
            splittedText = array_split(originalText, splitN)
            for text in splittedText:
                if (len(text) > 1024):
                    translatedTexts.extend(text)
                    # TODO rever utilidade desse split
                    # splitN = math.ceil(len(text) / 1024)
                    # splittedText2 = array_split(text, splitN)
                    # for text2 in splittedText2:
                    #     translatedTexts.extend(translate_text(text2))
                else:
                    translatedTexts.extend(translate_text(text))

            replace_text_in_file(originalText, translatedTexts, data, filePath)
        else:
            translatedTexts = translate_text(originalText)

            replace_text_in_file(originalText, translatedTexts, data, filePath)

def removeBackWord(word: str):
    if (len(word) > 0 and word[0] in ['!', '.', '#', ',', '?', ':']):
        word = word[1:len(word)]
        return removeBackWord(word)
    else:
        return word

def removeEndWord(word: str):
    if (len(word) > 0 and word[len(word)-1] in ['!', '.', '#', ',', '?', ':']):
        word = word[0:len(word)-1]
        return removeEndWord(word)
    else:
        return word
    
def check_directories(pathToTranslate: str):
    for path in glob.glob(pathToTranslate):
        if '.' not in path:
            print(rf"diretorio: {path}")
            check_directories(path + '/*')
        elif '.yml' in path:
            print(rf"traduz: {path}")
            translate_file(path)

if __name__ == "__main__":
    # Inicio do programa

    # ((?<!\[)\b\S+\b(?![\]])) ou \b[^\[^\]]*(?![^\[]*\])\b regex para obter texto que não está em colchetes
    # ("[^"]*") ou (?<=(["\']))(?:(?=(\\?))\2.)*?(?=\1), (?<=(["\'])).*?(?=\1) ou (?<=(["\']))(.*)(intro)(.*)+?(?=\1) regex para obter texto entre aspas
    # (?:(?<=\s)|(?<=^))([$]{1,2})[^\$]*\1(?=\s|$) exemplo de lookahead

    root = (len(sys.argv) > 1 and sys.argv[1]) or '*'
    root = root.replace('\\','/')

    check_directories(root)
        