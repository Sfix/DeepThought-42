# Crée le main du bot

import os
import sys
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import PrefixHandler
from telegram.ext import MessageHandler, Filters
import robot

#? Système de débuggage
# TODO: A supprimer en production.
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
logger = logging.getLogger()


# Initialise en fonction du lancement.
mode = os.getenv("MODE")
TOKEN = os.getenv("TOKEN")
if mode == "dev":
    def run(updater):
        updater.start_polling()
elif mode == "prod":
    def run(updater):
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("telegram-deepthought-42")
        # Code from https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#heroku
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))
else:
    logger.error("No MODE specified!")
    sys.exit(1)


# Initialise le Bot
dt42 = robot.Robot()
logger.info("Bot lancé")

#
# Définition des commandes que comprends le Bot
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

start_handler = CommandHandler(dt42.ordreStart, dt42.start)
dispatcher.add_handler(start_handler)

stop_handler = CommandHandler(dt42.ordreStop, dt42.stop)
dispatcher.add_handler(stop_handler)

stat_handler = CommandHandler(dt42.ordreStat, dt42.stat)
dispatcher.add_handler(stat_handler)


# Les '/+1', '/-1' et autres '/👍' ne passent pas dans CommandHandler
# Nous utilisons donc le prefix
plusOne_handler = PrefixHandler('/', dt42.ordrePlusOne, dt42.text)
dispatcher.add_handler(plusOne_handler)
minusOne_handler = PrefixHandler('/', dt42.ordreMinusOne, dt42.text)
dispatcher.add_handler(minusOne_handler)



if __name__ == '__main__':
    run(updater)
