#!/usr/bin/python
# -*- coding: utf-8 -*-

import locale

locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
# from telegram import Emoji, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Filters
import telegram
from telegram import ReplyKeyboardMarkup
from telegram.constants import ChatAction, ParseMode
import os
import redis
from trash_utils import *
import traceback
from icalendar import Calendar
from datetime import *
from datetime import datetime
from temp_utils import plot
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger('httpx').setLevel(logging.WARNING)

# YES, NO = (Emoji.THUMBS_UP_SIGN, Emoji.THUMBS_DOWN_SIGN)
# e.g. LIST_OF_ADMINS: "12313,34534,563355"
LIST_OF_ADMINS = [int(user_id.strip()) for user_id in os.environ.get('ADMIN_IDS', '').split(',') if user_id]
    
# e.g. LIST_OF_PLACES: "Eckstraße:12:123123;Kaiserstraße:5b:234234,2344343"
LIST_OF_PLACES = {}
for places in os.environ.get('PLACES', '').split(';'):
    if places:
        parts = places.split(':')
        ids = parts[2].split(',')
        for user_id in ids:
            print(user_id, parts[0], parts[1])
            LIST_OF_PLACES[int(user_id)] = {
                'street': parts[0],
                'house': parts[1]
            }
    
MARKUP_TRASH = "Müll"
MARKUP_PAPER = "Papier"
MARKUP_TEMP_YESTERDAY = "Temp: Gestern"
MARKUP_TEMP_TODAY = "Temp: Heute"
MARKUP_TEMP_WEKK = "Temp: Woche"
MARKUP_TEMP = [MARKUP_TEMP_YESTERDAY, MARKUP_TEMP_TODAY, MARKUP_TEMP_WEKK]

cache = redis.Redis(host=os.environ.get('REDIS_HOST', default='127.0.0.1'), port=6379, db=0)
cache.set_response_callback('HGET', pickle.loads)

logger.info("Telegram bot starting..")

async def _start(update):
    #    reply_markup = InlineKeyboardMarkup(
    #                [[InlineKeyboardButton('Free disk space', callback_data='free'),
    #                  InlineKeyboardButton('Start', callback_data='start')]])
    await update.message.reply_text("Welcome :)")


#                            reply_markup=reply_markup)

def _getMarkup(user_id):
    if user_id in LIST_OF_ADMINS:
        custom_keyboard = [[MARKUP_TRASH, MARKUP_PAPER],
                           MARKUP_TEMP]
    else:
        custom_keyboard = [['Müll',
                            'Papier']]
    return ReplyKeyboardMarkup(custom_keyboard)


async def start(update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = _getMarkup(update.message.from_user.id)
    await update.message.reply_text('Hi {0}! :)'.format(update.message.from_user.first_name),
                    reply_markup=reply_markup)
    await _start(update)


async def send_message(update, text, parse_mode, reply_markup):
    try:
        await update.message.reply_text(text, parse_mode=parse_mode, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Sending Message as {parse_mode} failed!\n{text}")
        logger.error(e)


async def write_time(update, context: ContextTypes.DEFAULT_TYPE):
    user_id = int(update.message.from_user.id)
    reply_markup = _getMarkup(user_id)
    text = update.message.text

    await context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    if text == 'id':
        await send_message(update, f'Your ID is {update.message.from_user.id}', None, reply_markup)
    if text == MARKUP_TRASH:
        msg = 'Access denied'
        print(user_id)
        if user_id in LIST_OF_PLACES.keys():
            place = LIST_OF_PLACES[user_id]
            (msg, success) = parseMull(street=place['street'], house_number=place['house'])
            if success:
                logger.debug("Success: %s" % msg)
            else:
                logger.warning("Failed: %s" % msg)

        await send_message(update, msg, ParseMode.HTML, reply_markup)

    elif text == MARKUP_PAPER:
        msg = "Papier-Leerungen:\n"
        try:
            year = datetime.today().year
            r = requests.get(os.environ.get('PAPIER_URL').format(year=year))
            text = r.text
        except Exception as e:
            msg = "An error occured:\n%s\n%s" % (e, traceback.format_exc())
            logger.error(msg)
            await update.message.reply_text(msg, reply_markup=reply_markup)
        try:
                gcal = Calendar.from_ical(text)
                dates = []
                closest_date = None
                for c in gcal.walk():
                    if c.name == 'VEVENT':
                        cur_date = c.get('DTSTART').dt.date()
                        logger.debug(cur_date)
                        line = cur_date.strftime("%a, %d.%m.%y")
                        if date.today() <= cur_date and closest_date == None:
                            closest_date = cur_date
                            msg += "-> %s\n" % line
                        else:
                            msg += "%s\n" % line
                        dates.append(cur_date)
                await send_message(update, msg, ParseMode.HTML, reply_markup)
        except Exception as e:
            msg = "An error occured:\n%s\n%s" % (e, traceback.format_exc())
            logger.error(msg)
            await update.message.reply_text(msg, reply_markup=reply_markup)

    elif text in MARKUP_TEMP and user_id in LIST_OF_ADMINS:
        msg = "No temperature recorded!"
        try:
            if cache.exists('temp'):
                last_time, temp = cache.hget('temp', 'temp')
                temp_rounded = round(float(temp), 1)
                last_time = "{0:%d.%m.%y %H:%M:%S}".format(last_time)
                l = load_list(cache)
                if l:
                    if text == MARKUP_TEMP_YESTERDAY:
                        yesterday_start = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0)
                        yesterday_end = yesterday_start.replace(hour=23, minute=59, second=59)
                        xvalues, yvalues = zip(*[(time, value) for (time, value) in l if yesterday_start < time < yesterday_end])
                    elif text == MARKUP_TEMP_TODAY:
                        today_start = datetime.now().replace(hour=0, minute=0, second=0)
                        xvalues, yvalues = zip(*[(time, value) for (time, value) in l if today_start < time])
                    else:
                        xvalues, yvalues = zip(*l)
                    num = len(xvalues)

                    msg = f"Last temperature: <b>{str(temp_rounded)}°C</b> ({last_time})\nList has <b>{num}</b> entries"

                    photo = plot(yvalues, xvalues)
                    await update.message.reply_photo(photo=photo, caption=msg, parse_mode=ParseMode.HTML,
                                reply_markup=reply_markup)
                    photo.close()
                else:
                    await send_message(update, 'Kein Werte gefunden', ParseMode.HTML, reply_markup)
            else:
                await send_message(update, msg, ParseMode.HTML, reply_markup)
        except Exception as e:
            msg = "An error occured:\n%s\n%s" % (e, traceback.format_exc())
            logger.error(msg)
            await update.message.reply_text(msg, reply_markup=reply_markup)
    elif text == 'ID':
        await update.message.reply_text(update.message.from_user.id, reply_markup=reply_markup)

    else:
        await start(update, context)


application = ApplicationBuilder().token(os.environ.get('BOT_TOKEN')).build()

application.add_handler(CommandHandler('start', start))

application.add_handler(MessageHandler(filters.TEXT | filters.COMMAND, write_time))

logger.info("Starting bot..")
application.run_polling()
