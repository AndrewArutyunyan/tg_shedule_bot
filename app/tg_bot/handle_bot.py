"""
This example shows how to use webhook with SSL certificate.
"""
import os
import ssl
import sys
from os import getenv
from datetime import datetime, timedelta
from time import strptime
from time import time
import yaml
import logging
import logging.handlers

from aiohttp import web

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import FSInputFile, Message, ContentType, KeyboardButton, reply_keyboard_remove
from aiogram.utils.markdown import hbold
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.methods import SetMyDescription
from aiogram import F

# from app.adapters.cron import add_cron_job, remove_cron_job, list_cron_jobs, list_today_jobs
from app.common.models import *
from app.common.common_functions import *


sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# Bot token can be obtained via https://t.me/BotFather
TOKEN_FILE = "config/token.txt"
TOKEN_FILE = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), TOKEN_FILE))
with open(TOKEN_FILE, 'r') as file:
    TOKEN = file.read()

# Webserver settings
# bind localhost only to prevent any external access
WEB_SERVER_HOST = "179.43.151.16"
# Port for incoming request from reverse proxy. Should be any available port
WEB_SERVER_PORT = 8443

# Path to webhook route, on which Telegram will send requests
WEBHOOK_PATH = "/webhook"
# Secret key to validate requests from Telegram (optional)
WEBHOOK_SECRET = "my-secret"
# Base URL for webhook will be used to generate webhook URL for Telegram,
# in this example it is used public address with TLS support
BASE_WEBHOOK_URL = "179.43.151.16"

# Path to SSL certificate and private key for self-signed certificate.
WEBHOOK_SSL_CERT = "config/tg_public.pem"
WEBHOOK_SSL_CERT = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), WEBHOOK_SSL_CERT))
WEBHOOK_SSL_PRIV = "config/tg_private.key"
WEBHOOK_SSL_PRIV = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), WEBHOOK_SSL_PRIV))

# Functionality-related definitions
TIMEZONE_OFFSET = 1 # GMT+1 for Austria
NOTIFICATION_TIMEDELTA_MIN = 15 # 15 min before event ! Change also in shedule_cron
GREETING_MSG = f"""
This bot helps you to manage your schedule.
Set new assignment and specify time, day of the week and a description with the command: {hbold("schedule [time] [day of the week] [description]")}.
Time should be in the ISO format HH:mm.
    Example: schedule 14:00 Tuesday English lesson

Set one-time event with the command: {hbold("once [datatime] [description]")} in the ISO format yyyy-MM-dd HH:mm.
    Example: once 2024-02-10 18:30 Doctor appointment.

Remove a planned one-time or periodic event by specifing its description or id with the command {hbold("remove [description/id]")}.
Id lookup table could be fetched by {hbold("list")} command.
    Examples: remove English lesson, remove 843099249

Disable one eventfrom a serie by specifing its description AND datetime with the command {hbold("disable [description] [datetime]")}.
    Examples: disable English lesson 2024-02-10 18:30.

List all planned tasks with the command {hbold("list")}.

List today's planned tasks with the command {hbold("today")}.
"""
GREETING_MSG_SHORT = """
Hello, this is Tutor to Student interaction bot! 
It will keep you on track with payment reminders, sheduling and probably more...
"""
STATE = "Start"

# Logging
logger = logging.getLogger()
fhandle = logging.handlers.TimedRotatingFileHandler('shedule_bot.log',  when='midnight')
shandle = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fhandle.setFormatter(formatter)
shandle.setFormatter(formatter)
logger.addHandler(fhandle)
logger.addHandler(shandle)
logger.setLevel(logging.INFO)


def get_job_id() -> int:
    return round(time()*1000)


# All aiogram handlers should be attached to the Router (or Dispatcher)
router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    kb = [
        [types.KeyboardButton(text="Student")],
        [types.KeyboardButton(text="Tutor")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
    await message.answer("Are you a student or a tutor?", 
                         reply_markup=keyboard)


@router.message(F.text == "Tutor")
async def command_tutor_handler(message: Message) -> None:
    """
    This handler receives messages with answer `Tutor` to the question Are you a student or a tutor?
    """
    tutor_name = message.from_user.full_name
    tutor = Tutor(chat_id=message.chat.id, full_name=tutor_name, phone_number=' ')
    is_added = add_tutor(tutor)
    if is_added == 0:
        set_chat_state(message.chat.id, "TUTOR")
        await message.answer(f"Welcome back, {tutor_name}! Upload new students book", 
                             reply_markup=reply_keyboard_remove.ReplyKeyboardRemove(remove_keyboard=True))
    elif  is_added == 1:
        set_chat_state(message.chat.id, "TUTOR")
        example_book = "received_xlsx/shedule_example.xlsx"
        file = FSInputFile(example_book, filename="shedule_example.xlsx")
        await message.answer_document(document=file, 
                                      caption=f"Greetings, {tutor_name}! " + \
                                        "Upload an Excel book with a shedule for the current month. Example attached", 
                                        reply_markup=reply_keyboard_remove.ReplyKeyboardRemove(remove_keyboard=True))
    else:
        await message.answer(f"Error occured, sorry contact the support contact from the description", 
                             reply_markup=reply_keyboard_remove.ReplyKeyboardRemove(remove_keyboard=True))


@router.message(F.text == "Student")
async def command_student_handler(message: Message) -> None:
    """
    This handler receives messages with answer `Student` to the question Are you a student or a tutor?
    """
    set_chat_state(message.chat.id, "UNIQUE_ID")
    await message.answer(f"Provide the unique ID from your tutor please", 
                         reply_markup=reply_keyboard_remove.ReplyKeyboardRemove(remove_keyboard=True))    


@router.message(F.text == "Shedule")
async def command_shedule_handler(message: Message) -> None:
    """
    This handler answers button `Shedule`
    """

    await message.answer("Not implemented yet")    


@router.message(F.text == "Payment")
async def command_shedule_handler(message: Message) -> None:
    """
    This handler answers button `Payment`
    """
    amount, currency = get_student_payment(message.chat.id)
    await message.answer(f"For the next month you'll have to pay {amount} {currency}")    


@router.message(F.document)
async def doc_handler(message: types.Message, bot:Bot) -> None:
    document = message.document
    logger.info("Received a file: " + document.file_name)
    if document.file_name.endswith(".xlsx"):
        file_id = document.file_id
        file = await bot.get_file(file_id)
        await bot.download_file(
            file.file_path,
            "received_xlsx/shedule_new.xlsx"
        )
        tutor = get_tutor_by_chat_id(message.chat.id)
        if tutor is None:
            await message.answer("The file is OK, but we couldn't read your profile from the database, error occured")
        else:
            students = update_students_from_excel("received_xlsx/shedule_new.xlsx", tutor)
            remove_outdated_students(students)
            update_notifications(tutor)
            if students is not None:
                student_names = [s.unique_id for s in students]
                await message.answer("✅ Successfully added the following students: \n\t- " + "\n\t- ".join(student_names))

    else:
        logger.warning("Filetype is unsupported")
        await message.answer("❌ Unsupported file format")


@router.message()
async def new_message_handler(message: types.Message) -> None:
    """
    Handler will answer user inputs

    Ignore another message types (like text, photo, sticker etc.)
    """
    chat_id=message.chat.id
    user_id = message.from_user.id
    request = message.text
    state = get_chat_state(message.chat.id)
    if state is None or state == "START":
        set_chat_state(message.chat.id, "START")
        await command_start_handler(message)

    elif state == "UNIQUE_ID":
        student_unique_id = message.text
        result = update_student_contact(unique_id=student_unique_id,
                                        chat_id=chat_id,
                                        phone_number=' ')
        kb = [
            [types.KeyboardButton(text="Payment")],
            [types.KeyboardButton(text="Shedule")]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
        if result == 0:
            await message.answer("❌ Such user was not found, please contact the tutor for the valid user_id")
        elif result == 1:
            await message.answer(f"✅ Welcome, {message.from_user.full_name}. I'll remind you about the next payment", 
                            reply_markup=keyboard)
        else:
            await message.answer("❌ An error occured and the user was not found, please contact the tutor")
        set_chat_state(message.chat.id, "STUDENT")

    elif state == "STUDENT":
        kb = [
            [types.KeyboardButton(text="Payment")],
            [types.KeyboardButton(text="Shedule")]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
        await message.answer("Sorry, didn't understad that", 
                            reply_markup=keyboard)
    
    else:
        "Something went wrong, please contact the tutor"

    

    # try:
    #     request_content = request.split(" ")
    #     if request_content[0].lower() == "schedule":
    #         event_time_str = request_content[1]
    #         event_time = datetime.strptime(event_time_str, "%H:%M")
    #         try:
    #             event_time = datetime.strptime(event_time_str, "%H:%M")
    #         except ValueError:
    #             event_time = datetime.strptime(event_time_str, "%-H:%M")
    #         event_time -= timedelta(hours=TIMEZONE_OFFSET)
    #         event_time -= timedelta(minutes=NOTIFICATION_TIMEDELTA_MIN)

    #         event_period_str = request_content[2]
    #         event_period = (strptime(event_period_str, "%A").tm_wday + 1) % 7
    #         event_desc = " ".join(request_content[3:])

    #         new_job_id = get_job_id()

    #         # with open(DB_FILE,'r') as yamlfile:
    #         #     db_yaml = yaml.safe_load(yamlfile) # Note the safe_load

    #         # if db_yaml is None:
    #         #     db_yaml = {user_id:[new_job_id]}
    #         # if user_id not in db_yaml.keys():
    #         #     db_yaml.update({user_id:[]})
    #         # db_yaml[user_id].append(new_job_id)

    #         cron_time = f"{event_time.minute} {event_time.hour} * * {event_period}"
    #         msg_to_send = event_desc

    #         add_cron_job(cron_period=cron_time, chat_id=chat_id, message=msg_to_send, id=new_job_id)

    #         # if db_yaml:
    #         #     with open(DB_FILE,'w') as yamlfile:
    #         #         yaml.safe_dump(db_yaml, yamlfile) # Also note the safe_dump
                    
    #         event_time += timedelta(hours=TIMEZONE_OFFSET)
    #         event_time += timedelta(minutes=NOTIFICATION_TIMEDELTA_MIN)

    #         logger.info(f"set a job for {cron_time}")
    #         logger.info(
    #             f"Set an occuring event for {event_time.strftime('%H:%M')} {event_period_str}s: {event_desc}")
            
    #         await message.answer(
    #             f"✅ Set an occuring event for {event_time.strftime('%H:%M')} {event_period_str}s: {event_desc}")
        
    #     elif request_content[0].lower() == "once":
    #         event_datetime_str = " ".join(request_content[1:3])
    #         try:
    #             event_datetime = datetime.strptime(event_datetime_str, "%Y-%m-%d %H:%M")
    #         except ValueError:
    #             event_datetime = datetime.strptime(event_datetime_str, "%Y-%m-%-d %H:%M")

    #         event_desc = " ".join(request_content[3:])

            
    #         event_datetime -= timedelta(hours=TIMEZONE_OFFSET)
    #         event_datetime -= timedelta(minutes=NOTIFICATION_TIMEDELTA_MIN)

    #         new_job_id = get_job_id()

    #         cron_time = f"{event_datetime.minute} {event_datetime.hour} {event_datetime.day} {event_datetime.month} *"
    #         msg_to_send = event_desc

    #         add_cron_job(cron_period=cron_time, chat_id=chat_id, message=msg_to_send, id=new_job_id)
                    
    #         event_datetime += timedelta(hours=TIMEZONE_OFFSET)
    #         event_datetime += timedelta(minutes=NOTIFICATION_TIMEDELTA_MIN)
    #         logger.info(f"set a job for {cron_time}")
    #         logger.info(
    #             f"Set a one-time event for {event_datetime}: {event_desc}")
    #         await message.answer(
    #             f"✅ Set a one-time event for {event_datetime}: {event_desc}")
        
    #     elif request_content[0].lower() == "remove":
    #         event_desc_or_id_str = " ".join(request_content[1:])
    #         event_desc = None
    #         event_id = None
    #         try:
    #             event_id = int(event_desc_or_id_str)
    #         except ValueError:
    #             event_desc = event_desc_or_id_str

    #         remove_cron_job(chat_id=chat_id, id=event_id, desc=event_desc)

    #         logger.info(
    #             f"Removed event: {event_desc_or_id_str}")
    #         await message.answer(
    #             f"✅ Removed event: {event_desc_or_id_str}")
        
    #     elif request_content[0].lower() == "disable":
    #         event_desc = " ".join(request_content[1:-2])
    #         event_datetime_str = " ".join(request_content[-2:])
    #         try:
    #             event_datetime = datetime.strptime(event_datetime_str, "%Y-%m-%d %H:%M")
    #         except ValueError:
    #             event_datetime = datetime.strptime(event_datetime_str, "%Y-%m-%-d %H:%M")
            
    #         logger.info(
    #             f"Not implemented, tried to: Disabled event: {event_desc} for {event_datetime}")
    #         await message.answer(
    #             f"❌ Not implemented, tried to: Disable event: {event_desc} for {event_datetime}")
        
    #     elif request_content[0].lower() == "list":
    #         events_list = "Currently scheduled [id: description]:\n"

    #         cur_jobs = list_cron_jobs(chat_id)
    #         for job_id, job_dec in cur_jobs.items():
    #             events_list += f" - {job_id}: {job_dec}\n"
    #         if len(cur_jobs.items()) == 0:
    #             events_list += "Nothing"

    #         await message.answer(events_list)
        
    #     elif request_content[0].lower() == "today":
    #         events_list = "Today scheduled [id: description time]:\n"

    #         cur_jobs = list_today_jobs(chat_id)
    #         for job_id, job_dec in cur_jobs.items():
    #             events_list += f" - {job_id}: {job_dec}\n"
    #         if len(cur_jobs.items()) == 0:
    #             events_list += "Nothing"

    #         await message.answer(events_list)
            
    #     else:
    #         await message.answer("❌ Unsupported format")
            
    # except Exception:
    #     logger.exception(f"Error handling request: {request}")
    #     # But not all the types is supported to be copied so need to handle it
    #     await message.answer("❌ Unsupported format")


async def send_message(id:int, message:str):
    """
    Send a text message to specific chat_id
    """
    print(id)
    async with Bot(token=TOKEN).context() as bot:
        await bot.send_message(text=message, chat_id=id)    
    # await operator.close()


async def on_startup(bot: Bot) -> None:
    # In case when you have a self-signed SSL certificate, you need to send the certificate
    # itself to Telegram servers for validation purposes
    # (see https://core.telegram.org/bots/self-signed)
    # But if you have a valid SSL certificate, you SHOULD NOT send it to Telegram servers.
    await bot.set_webhook(
        f"{BASE_WEBHOOK_URL}:{WEB_SERVER_PORT}{WEBHOOK_PATH}",
        certificate=FSInputFile(WEBHOOK_SSL_CERT),
    )

    await bot.set_my_description(GREETING_MSG_SHORT)



def run_tg_bot() -> None:
    """
    Set up the websocket server for telegram bot communication
    """
    # Dispatcher is a root router
    dp = Dispatcher()
    # ... and all other routers should be attached to Dispatcher
    dp.include_router(router)

    # Register startup hook to initialize webhook
    dp.startup.register(on_startup)

    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

    # Create aiohttp.web.Application instance
    app = web.Application()

    # Create an instance of request handler,
    # aiogram has few implementations for different cases of usage
    # In this example we use SimpleRequestHandler which is designed to handle simple cases
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    # Register webhook handler on application
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    # Mount dispatcher startup and shutdown hooks to aiohttp application
    setup_application(app, dp, bot=bot)

    # Generate SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)

    # And finally start webserver
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT, ssl_context=context)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    run_tg_bot()