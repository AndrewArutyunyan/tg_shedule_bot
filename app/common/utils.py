from typing import List, Union
import logging
from datetime import datetime

from ..adapters.xls_parser import read_students_excel
from ..adapters.db_connector import execute_query
from ..common.models import Student, Tutor

logger = logging.getLogger(__name__)


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


def update_students_from_excel(filename:str, tutor:Tutor)->List:
    """
    Extract students information from the Excel file, 
    write to Database and return back the list.
    """
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
    