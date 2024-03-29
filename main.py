import os 
import logging

from app.tg_bot.handle_bot import run_tg_bot


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

run_tg_bot()
