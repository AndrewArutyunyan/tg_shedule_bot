from typing import List, Union
import logging
from datetime import datetime

from ..adapters.xls_parser import read_students_excel
from ..adapters.db import execute_query
from ..adapters.cron import *
from .models import Student, Tutor

logger = logging.getLogger(__name__)

NOTIFICATION_DAY = 25
NOTIFICATION_HOUR = 10

def add_tutor(tutor:Tutor)->int:
    """
    Checks if there is such tutor in BD, if not adds him.
    Returns status: 0 - Tutor is already present in BD
                    1 - Successfully added new tutor
                    None - error occured
    """
    tutor_read_query = f"SELECT tutor_id FROM tutor WHERE chat_id = {tutor.chat_id}"
    try:
        tutor_id = execute_query(tutor_read_query)
        if tutor_id is None or len(tutor_id) == 0:
            tutor_write_query = "INSERT INTO tutor(chat_id, full_name, phone_number, added_at) VALUES (" + \
                str(tutor.chat_id) + ", '" + \
                str(tutor.full_name) + "', '" + \
                str(tutor.phone_number) + "', '" + \
                str(datetime.now()) + "');"
            execute_query(tutor_write_query, writeonly=True)
            logger.info("Added new tutor")
            return 1
        else:
            return 0
    except Exception as exp:
        logger.exception(exp)
        return None


def get_tutor_by_chat_id(chat_id:int)->Tutor:
    """
    Read DB and return a Tutor object with the current information
    """
    try:
        tutor_read_query = f"SELECT tutor_id, full_name, phone_number FROM tutor WHERE chat_id = {chat_id}"
        tutor_db = execute_query(tutor_read_query)
        if tutor_db is None or len(tutor_db) == 0:
            logger.error(f"Tutor with chat_id = {chat_id} was not found!")
            return None
        else:
            tutor = Tutor(tutor_id=tutor_db[0][0],
                          chat_id=chat_id,
                          full_name=tutor_db[0][1],
                          phone_number=tutor_db[0][2])
            return tutor
    except Exception as exp:
        logger.exception(exp)
        return None


def update_students_from_excel(filename:str, tutor:Tutor)->List[Student]:
    """
    Extract students information from the Excel file, 
    write to Database and return back the list.
    """
    #TODO: import lessons
    #TODO: isolate students by tutor_id, allow no updates of another tutor's students
    try:
        tutor_read_query = f"SELECT tutor_id FROM tutor WHERE chat_id = {tutor.chat_id}"
        tutor_id = execute_query(tutor_read_query)
        if tutor_id is None or len(tutor_id) == 0:
            tutor_write_query = "INSERT INTO tutor(chat_id, full_name, phone_number, added_at) VALUES (" + \
                str(tutor.chat_id) + ", '" + \
                str(tutor.full_name) + "', '" + \
                str(tutor.phone_number) + "', '" + \
                str(datetime.now()) + "');"
            execute_query(tutor_write_query, writeonly=True)
            logger.info("Added new tutor")

        students_excel = read_students_excel(filename)
        for student in students_excel:
            student.tutor = tutor
        student_ids_excel = [str(s.unique_id) for s in students_excel]
        student_read_query = "SELECT DISTINCT unique_id FROM student WHERE unique_id IN ('" + \
            "', '".join(student_ids_excel) + \
            "');"
        students_ids_db = execute_query(student_read_query)
        if len(students_ids_db) == 0:
            students_ids_db = []
        else:
            students_ids_db = [s[0] for s in students_ids_db]
        for s_excel in students_excel:
            if s_excel.unique_id not in students_ids_db:
                student_write_query = "INSERT INTO student(tutor_id, unique_id, full_name, added_at) VALUES (" + \
                    str(tutor_id[0][0]) + ", '" + \
                    str(s_excel.unique_id) + "', '" + \
                    str(s_excel.full_name) + "', '" + \
                    str(datetime.now()) + "');"
                execute_query(student_write_query, writeonly=True)
                logger.info("Added new student " + s_excel.unique_id)
            else:
                student_update_query = "UPDATE student SET payment_amount = " + \
                    str(s_excel.payment_amount) + ", payment_currency = '" + \
                    str(s_excel.payment_currency) + "' WHERE  unique_id = '" + \
                    str(s_excel.unique_id) + "';"
                execute_query(student_update_query, writeonly=True)
                logger.info(f"Updated payment information of user {s_excel.unique_id}")

        return students_excel
    
    except Exception as exp:
        logger.exception(exp)
        return None
    

def update_student_contact(unique_id:str, chat_id:int, phone_number:str)->int:
    """
    Insert contact information about student to the BD.
    Returns status: 0 - no such unique_id found in BD, nothing to update
        1 - Successfully updated student information
        None - error occured
    """
    try:
        student_read_query = "SELECT DISTINCT student_id, tutor_id FROM student WHERE unique_id ='" + \
            str(unique_id) + "';"
        students_ids_db = execute_query(student_read_query)
        if len(students_ids_db) == 0:
            logger.warning('Wrong user ID provided, no such user in the BD')
            return 0
        else:
            student_write_query = "UPDATE student SET chat_id = " + \
                str(chat_id) + ", phone_number = '" + \
                str(phone_number) + "' WHERE  unique_id = '" + \
                str(unique_id) + "';"
            execute_query(student_write_query, writeonly=True)
            logger.info(f"Updated contact information of user {unique_id}")
            # Update notifications
            tutor = Tutor(tutor_id=students_ids_db[0][1])
            update_notifications(tutor)
            return 1
    except Exception as exp:
        logger.exception(exp)
        return None
    
    
def remove_outdated_students(students:List[Student])->None:
    """
    Clear students that are not in the list
    """
    students_to_delete = []
    student_ids = [s.unique_id for s in students]
    try:
        student_read_query = f"SELECT DISTINCT unique_id FROM student WHERE tutor_id = {students[0].tutor.tutor_id};"
        students_ids_db = execute_query(student_read_query)
        if students_ids_db is not None and len(students_ids_db)>0:
            for s in students_ids_db:
                if s[0] not in student_ids:
                    students_to_delete.append(s[0])
            student_delete_query = "DELETE FROM student WHERE unique_id IN ('" + \
                "', '".join(students_to_delete) + \
                "');"
            execute_query(student_delete_query, writeonly=True)
        logger.info(f"Deleted all outdated student records except {len(students)} names")

    except Exception as exp:
        logger.error("Failed to delete outdated students")
        logger.exception(exp)


def plus_month(dt:datetime, mon:int)->datetime:
    """
    Adds a calendar month to the given date
    Code from here:
        https://github.com/zulip/finbot/blob/master/monthdelta.py
    """
    day = dt.day
    # subract one because months are not zero-based
    month = dt.month + mon - 1
    year = dt.year + month // 12
    # now add it back
    month = month % 12 + 1
    if month == 2:
        if day >= 29 and not year%4 and (year%100 or not year%400):
            day = 29
        elif day > 28:
            day = 28
    elif month in (4, 6, 9, 11) and day > 30:
        day = 30
    try:
        return dt.replace(year, month, day)
    except ValueError:
        raise OverflowError('date value out of range')


def update_notifications(tutor:Tutor):
    """
    Clear all current notification and add new ones based on the updated student information
    """
    #TODO: update lessons
    # Remove outdated notifications
    notification_read_query = f"SELECT notification_id FROM notification WHERE tutor_id = {tutor.tutor_id};"
    notifications_db = execute_query(notification_read_query)
    for n in notifications_db:
        remove_cron_job(n[0])

    notifications_delete_query = f"DELETE FROM notification WHERE tutor_id = {tutor.tutor_id};"
    execute_query(notifications_delete_query, writeonly=True)

    # Read students from DB to update notifications for each of them
    student_read_query = f"SELECT DISTINCT student_id, chat_id, payment_amount, payment_currency FROM student WHERE tutor_id = {tutor.tutor_id};"
    students_db = execute_query(student_read_query)
    if students_db is not None and len(students_db)>0:
        for s in students_db:
            student_id = s[0]
            chat_id = s[1]
            payment_amount = s[2]
            payment_currency = s[3]
            if chat_id is not None:
                try:
                    datetime_this_month = datetime(datetime.now().year,datetime.now().month, NOTIFICATION_DAY, hour=NOTIFICATION_HOUR)
                except ValueError:
                    datetime_this_month = datetime(datetime.now().year,datetime.now().month, 28, hour=NOTIFICATION_HOUR)
                    logger.warning("Date of notification does not exists, the current month is shorter")
                datetime_plus_month = plus_month(datetime_this_month, 1)
                notification_text = f"Good morning, time to pay for the next month exercises. Your monthly payment is {payment_amount} {payment_currency}"

                # Update DB
                # For the current month
                notification_write_query = "INSERT INTO notification(tutor_id, student_id, notification_datetime, description, tg_message, added_at) VALUES (" + \
                        str(tutor.tutor_id) + ", " + \
                        str(student_id) + ", '" + \
                        str(datetime_this_month) + "', '" + \
                        "Payment" + "', '" + \
                        str(notification_text) + "', '" + \
                        str(datetime.now()) + "');"
                execute_query(notification_write_query, writeonly=True)
                # For the next month
                notification_write_query = "INSERT INTO notification(tutor_id, student_id, notification_datetime, description, tg_message, added_at) VALUES (" + \
                        str(tutor.tutor_id) + ", " + \
                        str(student_id) + ", '" + \
                        str(datetime_plus_month) + "', '" + \
                        "Payment" + "', '" + \
                        str(notification_text) + "', '" + \
                        str(datetime.now()) + "');"
                execute_query(notification_write_query, writeonly=True)

                # Read notifications IDs from DB
                notification_read_query = "SELECT notification_id FROM notification WHERE student_id = " + \
                        str(student_id) + " AND notification_datetime = '" + \
                        str(datetime_this_month) + "';"
                notifications_db = execute_query(notification_read_query)
                notification_cur_id = notifications_db[0][0]

                notification_read_query = "SELECT notification_id FROM notification WHERE student_id = " + \
                        str(student_id) + " AND notification_datetime = '" + \
                        str(datetime_plus_month) + "';"
                notifications_db = execute_query(notification_read_query)
                notification_next_id = notifications_db[0][0]
                    
                # Update Cron jobs
                cron_time = f"{0} {datetime_this_month.hour} {datetime_this_month.day} {datetime_this_month.month} *"
                add_cron_job(cron_time, chat_id,  notification_text, notification_cur_id)
                cron_time = f"{0} {datetime_plus_month.hour} {datetime_plus_month.day} {datetime_plus_month.month} *"
                add_cron_job(cron_time, chat_id,  notification_text, notification_next_id)
                logger.info("Added new notification for payment")


def get_student_payment(tg_chat_id:int)->tuple[float, str]:
    """Read from DB payment information

    Args:
        tg_chat_id (int): message.chat.id from telegram

    Returns:
        tuple[float, str]: amount, currency of payment
    """
    payment_read_query = f"SELECT payment_amount, payment_currency FROM student WHERE chat_id = {tg_chat_id}"
    payment_db = execute_query(payment_read_query)
    if payment_db is not None and len(payment_db)>0:
        amount = payment_db[0][0]
        currency = payment_db[0][1]
        return amount, currency
    else:
        logger.error(f"Could not read payment information for the user with chat_id {tg_chat_id}")
        return None


def get_chat_state(tg_chat_id:int)->str:
    """Read from DB current telegram chat state.

    Args:
        chat_id (int): message.chat.id from telegram

    Returns:
        str: possible options: START, USER, TUTOR, UNIQUE_ID
    """
    try:
        chat_read_query = f"SELECT chat_state FROM chat WHERE tg_chat_id = {tg_chat_id};"
        chat_state = execute_query(chat_read_query)
        if chat_state is not None and len(chat_state)>0:
            return chat_state[0][0]
        else:
            return None
    except Exception as exc:
        logger.exception(exc)
        return None


def set_chat_state(tg_chat_id:int, state:str):
    """Write to the DB current telegram chat state.

    Args:
        chat_id (int): message.chat.id from telegram
        state (str): possible options: START, USER, TUTOR, UNIQUE_ID
    """
    try:
        chat_delete_query = f"DELETE FROM chat WHERE tg_chat_id = {tg_chat_id}"
        execute_query(chat_delete_query, writeonly=True)

        chat_write_query = "INSERT INTO chat(tg_chat_id, chat_state, added_at) VALUES(" + \
                str(tg_chat_id) + ", '" + \
                str(state) + "', '" + \
                str(datetime.now()) + "');"
        execute_query(chat_write_query, writeonly=True)
    except Exception as exc:
        logger.exception(exc)


def get_students_list(tutor_chat_id:int)->List[Student]:
    """
    Extract a list of student of some tutor from the DB

    Args:
        tutor_chat_id (int): Chat_id of the tutor

    Returns:
        List[Student]: array of Student objects
    """
    get_students_query = f"""
        SELECT 
            student_id, 
            unique_id, 
            chat_id, 
            full_name, 
            phone_number, 
            payment_amount, 
            payment_currency
        FROM 
            student
        WHERE
            tutor_id = (SELECT tutor_id FROM tutor WHERE chat_id = {tutor_chat_id});
        """
    student_list = []
    try:
        students_db = execute_query(get_students_query)
        for s_db in students_db:
            student_list.append(Student(student_id=s_db[0],
                                        unique_id=s_db[1],
                                        chat_id=s_db[2],
                                        full_name=s_db[3],
                                        phone_number=s_db[4],
                                        payment_amount=s_db[5],
                                        payment_currency=s_db[6]))
    except Exception as exc:
        logger.exception(exc)
    return student_list