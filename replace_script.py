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

# print(glob.glob("*"))
# pattern = '"[^"]*"'
# 
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
        # testPattern = re.compile(rf'(?<=(["\'])|([\s])|([\$])|([\]])|([n])|([\!])|([\.]))(?=[^\[^\]]*(?![^\[]*\])\b){re.escape(text)}*?\b')
        testPattern = re.compile(rf'(?m)((\b|\\n){re.escape(text)}(\b|\\n))(?=[^"]*"(?:[^"\r\n]*"[^"]*")*[^"\r\n]*$)')
        textTranslated = ''
        if (isinstance(translatedTexts[index], str)):
            textTranslated = translatedTexts[index]
        else:
            textTranslated = translatedTexts[index].translated_text

        # print(f"text: {text} translated: {textTranslated}")
        found = False
        fakeData = data
        while fileN < len(fakeData):
            indexData = 0
            while indexPart < len(fakeData[fileN]): # textLine in enumerate(fakeData[fileN], start=indexPart):
                if re.search(testPattern, fakeData[fileN][indexPart]) is None:
                    print(text)
                    #indexData = indexData + 1
                    indexPart = indexPart + 1
                    continue
                    #print('plus ')
                else:
                    #print('here ')
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
        #data[fileN] = re.sub(testPattern, str.format(text2), data[fileN], 1)
        #data = data.replace(text, translatedTexts[index].translated_text)
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
    # testPattern = re.compile(rf'''(?<=(["\']))(.*)({re.escape('will be deleted. Are you sure?')})(.*)+?(?=\1)''')
    # print(re.finditer(rf'''(?<=(["\']))(.*)({re.escape('will be deleted. Are you sure?')})(.*)+?(?=\1)''', 'DELETE_GAME:0 "Delete Game" SAVE:0 "Save" DELETE:0 "Delete" DELETE_CONFIRMATION_DESC:0 "The savegame $NAME|V$ will be deleted. Are you sure?" CLOUDSAVE_UNVAVAILABLE_TOOLTIP:0 "Cloud saves are not available" SAVE_ENABLE_CLOUDSAVE_TOOLTIP:0 "Save to cloud" LOAD_CLOUDSAVE_TOOLTIP:0 "Cloud Save" LOAD_IRONMAN_TOOLTIP:0 "Ironman Save"', re.MULTILINE))
    # for matchNum, match in enumerate(re.findall(rf'''(?<=(["\'])).*({re.escape('will be deleted. Are you sure?')}).*?(?=\1)''', 'DELETE_GAME:0 "Delete Game" SAVE:0 "Save" DELETE:0 "Delete" DELETE_CONFIRMATION_DESC:0 "The savegame $NAME|V$ will be deleted. Are you sure?" CLOUDSAVE_UNVAVAILABLE_TOOLTIP:0 "Cloud saves are not available" SAVE_ENABLE_CLOUDSAVE_TOOLTIP:0 "Save to cloud" LOAD_CLOUDSAVE_TOOLTIP:0 "Cloud Save" LOAD_IRONMAN_TOOLTIP:0 "Ironman Save"', re.MULTILINE), start=1):
    #     print(match[1])
    #     for groupNum in range(0, len(match.groups())):
    #         groupNum = groupNum + 1
            
    #         print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))

    # print(re.search(testPattern, 'DELETE_GAME:0 "Delete Game" SAVE:0 "Save" DELETE:0 "Delete" DELETE_CONFIRMATION_DESC:0 "The savegame $NAME|V$ will be deleted. Are you sure?" CLOUDSAVE_UNVAVAILABLE_TOOLTIP:0 "Cloud saves are not available" SAVE_ENABLE_CLOUDSAVE_TOOLTIP:0 "Save to cloud" LOAD_CLOUDSAVE_TOOLTIP:0 "Cloud Save" LOAD_IRONMAN_TOOLTIP:0 "Ironman Save"'))
    # print(re.sub(testPattern, 'teste', 'DELETE_GAME:0 "Delete Game" SAVE:0 "Save" DELETE:0 "Delete" DELETE_CONFIRMATION_DESC:0 "The savegame $NAME|V$ will be deleted. Are you sure?" CLOUDSAVE_UNVAVAILABLE_TOOLTIP:0 "Cloud saves are not available" SAVE_ENABLE_CLOUDSAVE_TOOLTIP:0 "Save to cloud" LOAD_CLOUDSAVE_TOOLTIP:0 "Cloud Save" LOAD_IRONMAN_TOOLTIP:0 "Ironman Save"', 1))

    # obter texto entre aspas
    pattern = r'(?<=(["\'])).*?(?=\1)'
    # patterns = [r'(?<=(["\'])).*?(?=\1)', r'(?<=\#).+?(?=\#)', r'\b[^\[^\]]*(?![^\[]*\])\b', r'(?<=\$).+?(?=\$)']
    # CK3_Traducao_PT-BR/custom_localization/ai_value_custom_loc_l_english.yml

    smallfile = None
    data = [[]]
    part = -1
    splitN = 1
    with open(rf'{filePath}', "r", encoding="utf-8-sig") as bigfile:
        fileSize = len(bigfile.read())
        splitN = math.ceil(fileSize / 30000)
        bigfile.seek(0)
        for lineno, line in enumerate(bigfile):
            if lineno % linesPerFile == 0:
                part = part + 1
                data.append([])
                # data.append('')
            # data[part] = data[part] + line
            data[part].append(line)

    # f = open(rf"{filePath}", "r", encoding="utf-8-sig")
    # data2 = f.read()
    # fileSize = len(data2)
    # splitN = math.ceil(fileSize / 30000)
    # f.close()
    # texts = []
    texts2 = []
    matches1 = []
    matches2 = []
    matches3 = []
    matches4 = []
    matches5 =[]
    originalText = []

    # texts = re.compile(pattern).findall(data)
    # print(texts)
    # for pattern in patterns:
    for filePart in data:
        for fileLine in filePart:
            matches1.extend(re.finditer(pattern, fileLine, re.MULTILINE))
    #matches1 = re.finditer(pattern, data, re.MULTILINE)

    #pattern = r'(?<=\#).+?(?=\#)'

    # matches = re.finditer(pattern, 'activity_adventure_desc:0 "[ACTIVITY.GetOwner.GetTitledFirstName] is adventuring in the area." activity_adventure_owner:0 "Adventurer" ACTIVITY_MAP_ITEM_TOOLTIP:0 " adadadad #T adadad[ActivityMapItem.GetActivity.GetName]# #I Click to select#! # adadad# " ACTIVITY_WAITING:0 "Waiting to start"', re.MULTILINE)
    
    # for matchNum, match in enumerate(matches, start=1):
    #     text = match.group()
    #     print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
    #     #texts2 = re.findall(pattern, text)
    # pattern = r'\b[^\#^\[^\]]*(?![^\#]*\]\#)\b'
    
    for matchNum, match in enumerate(matches1, start=1):
        text = match.group()
        len(text) > 0 and matches2.extend(remove_bracket(text))
        # print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
        # texts2 = re.findall(pattern, text)
        # for text2 in texts2:
        #     len(text2) > 0 and originalText.append(text2)
        # for groupNum in range(0, len(match.groups())):
        #     groupNum = groupNum + 1
            
        #     print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))

    # for match in matches2:
    #     matches3.extend(remove_bracket(match))

    for match in matches2:
        matches3.extend(remove_amp(match))

    for match in matches3:
        matches4.extend(remove_breakline(match))
    
    for match in matches4:
        matches5.extend(remove_reticence(match))   
    # pattern = r'\b[^\$^\#^\[^\]]*(?![^\$^\#^\[]*[\$\#\]])\b'

    for text in matches5:
        if len(text) > 0:
            text = removeEndWord(text)
            # if (len(text) > 0 and text[0] in ['!', '.', '#', ',', '?', ':']):
            #     text = text[1:len(text)]
            text = removeBackWord(text)
            if (len(text) > 0 and text[0] == ' '):
                text = text[1:len(text)] 
            if (text not in [' ', '\n', '']):
                originalText.append(text)

    translatedTexts = []
    # return print(originalText)
    if len(originalText) > 0:
        if (splitN > 1):
            splittedText = array_split(originalText, splitN)
            for text in splittedText:
                if (len(text) > 1024):
                    translatedTexts.extend(text)
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
        # print(originalText)
        # print(translatedTexts)

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
    # print(glob.glob("*"))
    root = (len(sys.argv) > 1 and sys.argv[1]) or '*'
    root = root.replace('\\','/')
    #print(glob.glob(root))
    # var = 'You can form a'
    # test = re.compile(rf'(?<=(["\']))({re.escape(var)})*?(?=\1)')
    # data = re.sub(test, 'voce pode ', 
    # '"You can form a [hybrid_culture|E] with the [culture.GetCollectiveNoun]."')

    # print(re.escape(data))
    # pattern = r'(?=\#).+?\#'

    # matches = re.split(pattern, 'ACTIVITY_MAP_ITEM_TOOLTIP:0 " adadadad #T adadad[ActivityMapItem.GetActivity.GetName]# #I Click to select#! # adadad# " ACTIVITY_WAITING:0 "Waiting to start"', re.MULTILINE)
    # print(matches)
    # for matchNum, match in enumerate(matches, start=1):
    #     text = match.group()
    #     print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
    #     texts2 = re.findall(pattern, text)
        # for text2 in texts2:
        #     len(text2) > 0 and originalText.append(text2)
        # for groupNum in range(0, len(match.groups())):
        #     groupNum = groupNum + 1
            
        #     print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))
        
    check_directories(root)
    
    # Searching and replacing the text
    # using the replace() function
    # index = 0
    # for text in originalText:
    #     test = re.compile(rf"\b{re.escape(text)}\b")
    #     #data = re.sub(test, str.format(translatedTexts[index].translated_text), data)
    #     data = data.replace(text, translatedTexts[index].translated_text)
    #     index = index + 1
    # f.close()

    # with open(r'CK3_Traducao_PT-BR/event_localization/prison_events/prison_events_l_english.yml', 'w', encoding="utf-8") as file:
  
    #     # Writing the replaced data in our
    #     # text file
    #     file.write(data)
    #     file.close()
        