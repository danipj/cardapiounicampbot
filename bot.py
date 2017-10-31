#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import (Updater, CommandHandler)
import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime, timedelta
import re
import smtplib
import signal

######
######  Logger settings
######

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))

######
###### Auxiliary functions
######

def getMenuDict (text):
    index = 0
    menuOptions = {}
    isMenuOption = False

    for line in text:
        if "FEIJÃO" in line: # menu option begins with feijão - arroz could be dessert
            isMenuOption = True
            key = getKey(index)
            menuOptions[key] = []
        if isMenuOption:
            menuOptions[key].append(line)
        if "SUCO" in line: # option ends with suco
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
    soup = BeautifulSoup(htmlText, "html.parser")

    # split into list without ugly whitespace
    text = re.split(r'\s{2,}', soup.get_text())

    return text

def getDate():
    #get next meal date
    date = datetime.now()
    if date.weekday() == 5: # sabado
        delta = 2
    elif date.weekday() == 6: # domingo
        delta = 1
    #bandejao fechou, pegar proximo dia (+3 porque server está em UTC #gambiarra)
    elif date.hour >19+3 or (date.hour ==19+3 and date.minute >=45):
        if date.weekday() == 4: # sexta feira, pegar segunda
            delta = 3
        else:
            delta = 1
    else:
        delta = 0
    return datetime.today() + timedelta(days=delta)

######
###### Bot commands
######

def start(bot, update):
    update.message.reply_text(
        'Veja o cardápio do dia usando o comando /get\nPara o cardápio vegetariano, use /veg')

def get(bot, update):

    #get next meal date
    date = getDate()
    url = "http://www.prefeitura.unicamp.br/apps/site/cardapio.php?d=%s-%s-%s" % (date.year,date.month,date.day)

    text = getCleanText(url)
    menuDict = getMenuDict(text)

    update.message.reply_text("*%s/%s/%s*"%(date.day,date.month,date.year), parse_mode="Markdown")
    update.message.reply_text("*ALMOÇO*\n"+menuDict["Almoco"],parse_mode="Markdown")
    update.message.reply_text("*JANTA*\n"+menuDict["Jantar"],parse_mode="Markdown")

def veg(bot, update):

    #get next meal date
    date = getDate()
    url = "www.prefeitura.unicamp.br/apps/site/cardapio.php?d=%s-%s-%s" % (date.year,date.month,date.day)

    text = getCleanText(url)
    menuDict = getMenuDict(text)

    update.message.reply_text("*%s/%s/%s*"%(date.day,date.month,date.year), parse_mode="Markdown")
    update.message.reply_text("*ALMOÇO*\n"+menuDict["AlmocoVeg"],parse_mode="Markdown")
    update.message.reply_text("*JANTA*\n"+menuDict["JantarVeg"],parse_mode="Markdown")

def send_error_mail():
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    
    file = open("token.txt",'r')
    trash = file.readline()
    email = file.readline()
    pwd = file.readline()

    server.login(email.strip(), pwd.strip())
     
    msg = "CardapioBot stopped."
    server.sendmail(email, email, msg)
    server.quit()

def sign_handler(signal, frame):
    send_error_mail()
######
###### Main code
######

def main():

    #get security info from file
    file = open("token.txt",'r')
    token = file.readline()


    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token=token.strip(), user_sig_handler=sign_handler)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # simple start function
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("get", get))
    dp.add_handler(CommandHandler("veg", veg))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()

