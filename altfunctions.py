import requests
import re

def getMenuDict (text):
    index = 0
    menuOptions = {}
    isMenuOption = False

    for line in text:
        if "ARROZ" in line: # option begins
            isMenuOption = True
            key = getKey(index)
            menuOptions[key] = []
        if isMenuOption:
            menuOptions[key].append(line)
        if "SUCO" in line: # option ends
            isMenuOption = False
            index += 1 # next option

    for option in menuOptions: # lists to strings
        menuOptions[option] = "\n".join(menuOptions[option])

    return menuOptions

def getKey(index):
    if index == 0:
        return "Almoco"
    elif index == 1:
        return "AlmocoVeg"
    elif index == 2:
        return "Jantar"
    else:
        return "JantarVeg"

def getCleanText(url):
    # get and decode web content
    content = requests.get(url).content
    htmlText = content.decode('cp1252')

    # remove HTML
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(htmlText, "lxml")

    # split into list without ugly whitespace
    text = re.split(r'\s{2,}', soup.get_text())

    return text

text = getCleanText("http://catedral.prefeitura.unicamp.br/cardapio.php")
print getMenuDict(text)['Jantar']
