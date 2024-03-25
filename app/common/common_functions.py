from typing import List, Union
import logging
from datetime import datetime

from ..adapters.xls_parser import read_students_excel
from ..adapters.db_connector import execute_query
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
    tutor_read_query = f"SELECT tutor_id FROM tutor WHERE contact_id = {tutor.contact_id}"
    try:
        tutor_id = execute_query(tutor_read_query)
        if tutor_id is None or len(tutor_id) == 0:
            tutor_write_query = "INSERT INTO tutor(contact_id, full_name, phone_number, added_at) VALUES (" + \
                str(tutor.contact_id) + ", '" + \
                str(tutor.full_name) + "', '" + \
                str(tutor.phone_number) + "', '" + \
                str(datetime.now()) + "');"
            execute_query(tutor_write_query, readonly=True)
            logger.info("Added new tutor")
            return 1
        else:
            return 0
    except Exception as exp:
        logger.exception(exp)
        return None


def get_tutor_by_contact_id(contact_id:int)->Tutor:
    """
    Read DB and return a Tutor object with the current information
    """
    try:
        tutor_read_query = f"SELECT tutor_id, full_name, phone_number FROM tutor WHERE contact_id = {contact_id}"
        tutor_db = execute_query(tutor_read_query)
        if tutor_db is None or len(tutor_db) == 0:
            logger.error(f"Tutor with contact_id = {contact_id} was not found!")
            return None
        else:
            tutor = Tutor(tutor_id=tutor_db[0][0],
                          contact_id=contact_id,
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
        tutor_read_query = f"SELECT tutor_id FROM tutor WHERE contact_id = {tutor.contact_id}"
        tutor_id = execute_query(tutor_read_query)
        if tutor_id is None or len(tutor_id) == 0:
            tutor_write_query = "INSERT INTO tutor(contact_id, full_name, phone_number, added_at) VALUES (" + \
                str(tutor.contact_id) + ", '" + \
                str(tutor.full_name) + "', '" + \
                str(tutor.phone_number) + "', '" + \
                str(datetime.now()) + "');"
            execute_query(tutor_write_query, readonly=True)
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
                execute_query(student_write_query, readonly=True)
                logger.info("Added new student " + s_excel.unique_id)
            else:
                student_update_query = "UPDATE student SET payment_amount = " + \
                    str(s_excel.payment_amount) + ", payment_currency = '" + \
                    str(s_excel.payment_currency) + "' WHERE  unique_id = '" + \
                    str(s_excel.unique_id) + "';"
                execute_query(student_update_query, readonly=True)
                logger.info(f"Updated payment information of user {s_excel.unique_id}")

        return students_excel
    
    except Exception as exp:
        logger.exception(exp)
        return None
    

def update_student_contact(unique_id:str, contact_id:int, phone_number:str)->int:
    """
    Insert contact information about student to the BD.
    Returns status: 0 - no such unique_id found in BD, nothing to update
        1 - Successfully updated student information
        None - error occured
    """
    try:
        student_read_query = "SELECT DISTINCT student_id FROM student WHERE unique_id ='" + \
            str(unique_id) + "';"
        students_ids_db = execute_query(student_read_query)
        if len(students_ids_db) == 0:
            logger.warning('Wrong user ID provided, no such user in the BD')
            return 0
        else:
            student_write_query = "UPDATE student SET contact_id = " + \
                str(contact_id) + ", phone_number = '" + \
                str(phone_number) + "' WHERE  unique_id = '" + \
                str(unique_id) + "';"
            execute_query(student_write_query, readonly=True)
            logger.info(f"Updated contact information of user {unique_id}")
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
            execute_query(student_delete_query, readonly=True)
        logger.info(f"Deleted all outdated student records except {len(students)} names")

    except Exception as exp:
        logger.error("Failed to delete outdated students")
        logger.exception(exp)


def plus_month(dt:datetime, mon:int)->datetime:
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
    notifications_delete_query = f"DELETE FROM notification WHERE WHERE tutor_id = {tutor.tutor_id};"
    execute_query(notifications_delete_query, readonly=True)

    student_read_query = f"SELECT DISTINCT student_id, payment_amount, payment_currency FROM student WHERE tutor_id = {tutor.tutor_id};"
    students_db = execute_query(student_read_query)
    if students_db is not None and len(students_db)>0:
        for s in students_db:
            student_id = s[0]
            payment_amount = s[1]
            payment_currency = s[2]
            # Update Cron jobs
            # TODO: Update Cron jobs, write tests
            # Update DB
            try:
                datetime_now = datetime(datetime.now().year,datetime.now().month, NOTIFICATION_DAY, hour=NOTIFICATION_HOUR)
            except ValueError:
                datetime_now = datetime(datetime.now().year,datetime.now().month, 28, hour=NOTIFICATION_HOUR)
                logger.warning("Date of notification does not exists, the current month is shorter")
            datetime_plus_month = plus_month(datetime_now, 1)
            # For the current month
            notification_write_query = "INSERT INTO notification(tutor_id, student_id, notification_datetime, description, tg_message, added_at) VALUES (" + \
                    str(tutor.tutor_id) + ", " + \
                    str(student_id) + ", '" + \
                    str(datetime_now) + "', '" + \
                    "Payment" + "', '" + \
                    str(f"Good morning, time to pay for the next month exercises. \n Your monthly payment is {payment_amount} {payment_currency}") + "', '" + \
                    str(datetime.now()) + "');"
            execute_query(notification_write_query, readonly=True)
            # For the next month
            notification_write_query = "INSERT INTO notification(tutor_id, student_id, notification_datetime, description, tg_message, added_at) VALUES (" + \
                    str(tutor.tutor_id) + ", " + \
                    str(student_id) + ", '" + \
                    str(datetime_plus_month) + "', '" + \
                    "Payment" + "', '" + \
                    str(f"Good morning, time to pay for the next month exercises. \n Your monthly payment is {payment_amount} {payment_currency}") + "', '" + \
                    str(datetime.now()) + "');"
            execute_query(notification_write_query, readonly=True)
            logger.info("Added new notification for payment")

