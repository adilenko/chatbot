from dbhelper import DBHelper
from models import QuestionsList
from telegram.ext import Updater
import logging

db = DBHelper("chatbotDB")
TOKEN = "1056892394:AAGb7FVokUYC--nqYA9KgIKjExqL76W221o"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher
questionsList = QuestionsList()
usersDict = {}
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
