#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import (Updater, CommandHandler)
import requests
from bs4 import BeautifulSoup
import logging
#import re


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def start(bot, update):
    update.message.reply_text(
        'Veja o cardápio do dia usando o comando /get')

def get(bot, update):
    #update.message.reply_text("Checando cardápio")
    page = requests.get("http://catedral.prefeitura.unicamp.br/cardapio.php")
    update.message.reply_text("Cardápio encontrado")
    soup = BeautifulSoup(page.content,"html.parser")
    #remover tag br que só atrapalha
    #for e in soup.find_all('br'):
     #   e.extract()
    #achar tabelas
    cells = soup.find_all('table')

    name = ""
    for cell in cells:
        if "class" in cell.attrs and "fundo_cardapio" in cell['class'] :
            name += "------------------------------\n"
            for tag in cell.contents:
                if tag.name is not None and len(tag.contents)>0 :
                    #name += tag.name + "\n"
                    for tag1 in tag.contents:
                        if tag1.string is not None:
                            if len(tag1.string)>1:
                                name += tag1.string.strip() + "\n"
                        elif len(tag1.contents)>0:
                            for tag2 in tag1.contents:
                                if tag2.string is not None and len(tag2.string)>1:
                                    name += tag2.string.strip() + "\n"
               # else:
                   # name+=tag.string+"\n"
            #name = cell.prettify()
            #cardapio = re.sub("<\/?\w+\/?>","",name)
            #update.message.reply_text(cardapio.strip())
    #    if len(cell.contents)>1 and cell.contents[0].name is not None and "strong" in cell.contents[0].name.lower():
    #        name+= cell.contents[0].string + "\n"
      #  if cell.string is not None:
            #name = cell.string.encode('utf8')
          #  name += str(cell.string)+ "\n"
            #if "café da manhã" in name.lower():
             #   update.message.reply_text("Café")
              #  i = cells.index(cell)
               # update.message.reply_text(cells[i+1].string)

    #for i in range(i,i+4):
     #   string += cell[i].string + "\n"
    #name="fim"
    update.message.reply_text(name)

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))

def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token="435711787:AAHMugWJ4liav7RCMBcSMYRVbu2khc9C8BQ")

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