import sys
from typing import List, Dict, Union
from datetime import datetime, timedelta
import os
import logging

from crontab import CronTab


NOTIFICATION_TIMEDELTA_MIN = 15 # 15 min before event 
TIMEZONE_OFFSET = 1 # GMT+1 for Austria

logger = logging.getLogger(__name__)


def add_cron_job(cron_period:str, contact_id:int, message:str, notification_id:int):
    """Add a cron job to send telegram message

    Args:
        cron_period (str): standart cron formated time period
        contact_id (int): telegram chat id
        message (str): text to send via telegram
        notification_id (int): unique ID for that notification (uniqueness is not garanteed)
    """
    cron = CronTab(user='user')
    venv_path = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), 'venv/bin/python')
    script_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'send_sheduled_msg.py'))
    log_path = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'cron_errors.txt')
    job  = cron.new(command=f'{venv_path} {script_path} {contact_id} "{message}" >> {log_path}  2>&1', 
                    comment=str(notification_id))
    job.setall(cron_period)
    job.enable()
    cron.write()
    logger.debug("Cron job added")


def remove_cron_job(notification_id:int=None):
    """Removes cron notificaiton by provided id

    Args:
        notification_id (int): id set using add_cron_job funciton.
    """
    try:
        cron = CronTab(user='user')
        if notification_id is not None:
            cron.remove_all(comment=str(notification_id))
            cron.write()
            logger.debug("Cron job(s) removed")
        else:
            cron.remove_all()
            cron.write()
            logger.debug("Cron jobs removed")
    except Exception as exc:
        logger.exception(exc)


# def disable_cron_job(id:int, event_datatime:datetime):

def list_cron_jobs(contact_id:int=None, notification_id:Union[int,List[int]]=None)->Dict:
    """Returns the list of all active notifications for the given user 
    or from the given notification ids.
    If no arguments provided returns complete set of all cron jobs.

    Args:
        contact_id (int): telegram chat id
        notification_id (Union[int,List[int]], optional): one or an array of ids for each cron information is returned. 
            Defaults to None.

    Returns:
        Dict: _description_
    """
    cron = CronTab(user='user')
    out_jobs = {}

    if isinstance(notification_id, int):
        id_list = [notification_id]
    else:
        id_list = notification_id

    if notification_id is None:
        for job in cron:
            command = job.command.split(" ")
            contact_id_cron = int(command[2])
            notification_id_cron = int(job.comment)
            job_desc = " ".join(command[3:-4])[1:-1]
            if contact_id is None:
                out_jobs.update({notification_id_cron: job_desc})
            elif contact_id_cron == contact_id:
                out_jobs.update({notification_id_cron: job_desc})
    else:
        for job_id in id_list:
            for job in cron.find_comment(str(job_id)):
                command = job.command.split(" ")
                contact_id_cron = int(command[2])
                notification_id_cron = int(command[-1])
                job_desc = " ".join(command[3:-5])[1:-1]
                out_jobs.update({notification_id_cron: job_desc})
                
    return out_jobs


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
        logger.exception("Job cleanup failed.")


        