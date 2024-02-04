import asyncio
import sys
from typing import List, Dict, Union
from datetime import datetime, timedelta
import os
import logging
from croniter import croniter

from aiogram import Bot, Dispatcher

from crontab import CronTab


NOTIFICATION_TIMEDELTA_MIN = 15 # 15 min before event 
TIMEZONE_OFFSET = 1 # GMT+1 for Austria

MESSAGE_NOTIFICATION = f"⏰Your planned event is IN {NOTIFICATION_TIMEDELTA_MIN} MINUTES! "

def add_cron_job(cron_period:str, chat_id:int, message:str, id:int):
    cron = CronTab(user='user')
    job  = cron.new(command=f'/home/user/scripts/tg_bot/venv/bin/python /home/user/scripts/tg_bot/shedule_cron.py {chat_id} "{message}" >> /home/user/scripts/tg_bot/cron_errors.txt  2>&1', 
                    comment=str(id))
    job.setall(cron_period)
    job.enable()
    cron.write()

def remove_cron_job(chat_id:int, id:int=None, desc:str=None):
    # ! Description overrides id !
    jobs = list_cron_jobs(chat_id)
    if desc is not None:
        for job_id, job_desc in jobs.items():
            if job_desc == desc:
                id = job_id
                cron = CronTab(user='user')
                cron.remove_all(comment=str(id))
                cron.write()
    if id is not None and id in jobs.keys():
        cron = CronTab(user='user')
        cron.remove_all(comment=str(id))
        cron.write()


# def disable_cron_job(id:int, event_datatime:datetime):

def list_cron_jobs(chat_id:int, job_id:Union[int,List[int]]=None)->Dict:
    cron = CronTab(user='user')
    out_jobs = {}
    id_list = []
    if job_id is None:
        for job in cron:
            command = job.command.split(" ")
            chat_id_cron = int(command[2])
            job_id_cron = int(job.comment)
            job_desc = " ".join(command[3:-4])[1:-1]
            if chat_id_cron == chat_id:
                out_jobs.update({job_id_cron: job_desc})
    elif len(job_id) > 1:
        id_list = job_id
    else:
        id_list = [job_id]
    for job_id in id_list:
        for job in cron.find_comment(str(job_id)):
            command = job.command.split(" ")
            chat_id_cron = int(command[2])
            job_id_cron = int(command[-1])
            job_desc = " ".join(command[3:-5])[1:-1]
            if chat_id_cron == chat_id:
                out_jobs.update({job_id_cron: job_desc})
    return out_jobs

def list_today_jobs(chat_id:int):
    cron = CronTab(user='user')
    out_jobs = {}
    for job in cron:
        command = job.command.split(" ")
        chat_id_cron = int(command[2])
        job_id_cron = int(job.comment)
        job_desc = " ".join(command[3:-4])[1:-1]
        if chat_id_cron == chat_id:
            schedule = job.schedule(date_from=datetime.now())
            next_datetime = schedule.get_next()
            next_datetime = next_datetime + timedelta(minutes=NOTIFICATION_TIMEDELTA_MIN) \
                    + timedelta(hours=TIMEZONE_OFFSET)
            if next_datetime.day == datetime.now().day \
                and next_datetime.month == datetime.now().month \
                and next_datetime.year == datetime.now().year:
                out_jobs.update({job_id_cron: job_desc + " " + next_datetime.strftime("%H:%M")})
    return out_jobs


async def send_message(id:int, message:str):
    print(id)
    async with Bot(token=TOKEN).context() as bot:
        await bot.send_message(text=MESSAGE_NOTIFICATION + message, chat_id=id)    
    # await operator.close()

def cleanup():
    try:
        cron = CronTab(user='user')
        for job in cron:
            schedule = job.schedule(date_from=datetime.now())
            next_datetime = schedule.get_next()
            if (next_datetime - datetime.now()).days > 365:
                cron.remove(job)
        cron.write()
    except Exception:
        logging.exception("Job cleanup failed.")

if __name__ == '__main__':

    cleanup()

    args = sys.argv[1:]
    chat_dest = int(args[0])
    chat_msg = args[1]

    dir_path = os.path.dirname(os.path.realpath(__file__))
    # Bot token can be obtained via https://t.me/BotFather
    TOKEN_FILE = os.path.join(dir_path, "token.txt")
    with open(TOKEN_FILE, 'r') as file:
        TOKEN = file.read()

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    # print(chat_msg)
    asyncio.run(send_message(chat_dest, chat_msg))

        