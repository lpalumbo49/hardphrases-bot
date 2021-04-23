from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import re
import json
import pymongo
import logging

#pip3 install dnspython
#pip3 install pymongo

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

valid_authors = ['chori', 'juan', 'kemero', 'lucho', 'lukas', 'otros']

def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def insert_phrase(update, context):
    if len(context.args) < 2:
        update.message.reply_text("Sintaxis del comando: /insert_phrase <autor> <frase_hard>")
        return
    
    author = context.args[0].lower()
    if author not in valid_authors:
        update.message.reply_text("Debes enviar uno de estos nombres: " + str(valid_authors))
        return

    phrase = " ".join(context.args[1:])

    logger.info('Inserting phrase "%s" from "%s"', phrase, author)
    p = {"author": author, "phrase": phrase}

    try:
        client = get_mongo_client()
        collection = client.hard.facts
        collection.insert_one(p)

        update.message.reply_text(text=beautify_response(p))
    except Exception as e:
        print(e)        
    finally:
        client.close()        

def get_phrase(update, context):
    aggregation = [{"$sample": {"size": 20}}]
    author = ""
    
    if len(context.args) > 0:
        author = context.args[0].lower()
        aggregation.append({"$match": {"author": author}})

    logger.info('Getting phrase from "%s"', author)

    if author != "" and author not in valid_authors:
        update.message.reply_text("Debes enviar uno de estos nombres: " + str(valid_authors))
        return

    try:
        client = get_mongo_client()
        collection = client.hard.facts
        cursor = collection.aggregate(aggregation)

        p = list(cursor)[0]
        update.message.reply_text(beautify_response(p))
    except Exception as e:
        print(e)
    finally:
        client.close()    

def get_mongo_client():
    return pymongo.MongoClient("mongodb+srv://meli:DlBun4ffoGUpXNuP@meliexercisecluster-iihbu.mongodb.net/test?retryWrites=true")
    
def beautify_response(p):
    return p['author'].capitalize() + ": " + p['phrase']

def main():
    updater = Updater('666959502:AAEcchkF1c6bNWWij_gPMusBU1ubhLT6RcI')
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('insert_phrase', insert_phrase))
    dp.add_handler(CommandHandler('get_phrase', get_phrase))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
