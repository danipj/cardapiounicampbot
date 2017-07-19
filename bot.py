#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import (Updater, CommandHandler)
import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def start(bot, update):
    update.message.reply_text(
        'Veja o cardápio do dia usando o comando /get')

def get(bot, update):

    #get next meal date
    date = datetime.now()
    if date.hour >19 or (date.hour ==19 and date.minute >=45):
        #bandejao fechou, pegar proximo dia
        date = datetime.today() + datetime.timedelta(days=1)

    page = requests.get("http://catedral.prefeitura.unicamp.br/cardapio.php?d=%s-%s-%s" % (date.year,date.month,date.day))
    soup = BeautifulSoup(page.content,"html.parser")

    #achar tabelas
    tables = soup.find_all('table')

    name = ""
    for table in tables:
        #se ja tiver pegado a refeição, publica e zera string
        if len(name)>1:
            update.message.reply_text(name)
            name=""

        #achar a class especifica dentro da table
        if "class" in table.attrs and "fundo_cardapio" in table['class']:
            #html nao ajuda o beautifulsoup a achar o texto (.string), descer tag por tag
            for tag in table.contents:
                if tag.name is not None and len(tag.contents)>0 :
                    for tag1 in tag.contents:
                        if tag1.string is not None:
                            #varias strings são só whitespace, checar se é palavra
                            if len(tag1.string)>1:
                                name += tag1.string.strip() + "\n"
                        elif len(tag1.contents)>0:
                            for tag2 in tag1.contents:
                                if tag2.string is not None and len(tag2.string)>1:
                                    name += tag2.string.strip() + "\n"


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))

def main():
    
    #get token from file
    file = open("token.txt",'r')
    token = file.readline()

    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token=token.strip())

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # simple start function
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("get", get))

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