import os
import sys
import unittest
import logging
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.adapters.db import execute_query
from app.common.common_functions import *
from app.common.models import Tutor, Student


class TestXlsParser(unittest.TestCase):
    logger = logging.getLogger(__name__)
    logging.basicConfig(format = '%(asctime)s %(module)s %(levelname)s: %(message)s',
                    datefmt = '%m/%d/%Y %H:%M:%S', level = logging.INFO)

    def setUp(self) -> None:
        # Store the current log level to restore it later
        original_log_level = logging.getLogger().getEffectiveLevel()
        # Set the log level to a higher level, e.g., WARNING or CRITICAL
        logging.disable(logging.CRITICAL)

        self.tutor_id = 3
        self.student_id = 3
        self.tutor_chat_id = 252353213
        self.tutor_full_name = 'Tutor 2'
        self.tutor_phone_number = '23423523522'
        self.student_unique_id = 'Student_1'
        self.student_full_name = 'Student 1'
        self.payment_amount = 100
        self.payment_currency = "RUB"
        self.student_chat_id = 252353213
        tutor_delete_query = f"DELETE FROM tutor WHERE tutor_id = {self.tutor_id}"
        execute_query(tutor_delete_query, writeonly=True)
        student_delete_query = f"DELETE FROM student WHERE student_id = {self.student_id}"
        execute_query(student_delete_query, writeonly=True)
        tutor_write_query = "INSERT INTO tutor(tutor_id, chat_id, full_name, phone_number, added_at) VALUES (" + \
            str(3) + ", " + \
            str(self.tutor_chat_id) + ", '" + \
            str(self.tutor_full_name) + "', '" + \
            str(self.tutor_phone_number) + "', '" + \
            str(datetime.now()) + "');"
        execute_query(tutor_write_query, writeonly=True)
        tutor_read_query = f"SELECT tutor_id FROM tutor WHERE chat_id = {self.tutor_chat_id}"
        tutor_id = execute_query(tutor_read_query)
        student_write_query = "INSERT INTO student(student_id, tutor_id, chat_id, unique_id, full_name, payment_amount, payment_currency, added_at) VALUES (" + \
            str(3) + ", " + \
            str(tutor_id[0][0]) + ", " + \
            str(self.student_chat_id) + ", '" + \
            str(self.student_unique_id) + "', '" + \
            str(self.student_full_name) + "', " + \
            str(self.payment_amount) + ", '" + \
            str(self.payment_currency) + "', '" + \
            str(datetime.now()) + "');"
        execute_query(student_write_query, writeonly=True)

        # Restore the original log level after the tests
        logging.disable(original_log_level)

        return super().setUp()


    def test_add_tutor(self):
        """
        Try to add a new tutor in DB.
        Test passed if adding new tutor returns 0 (it was already added in DB).
        """
        tutor = Tutor(chat_id=self.tutor_chat_id, full_name=self.tutor_full_name, phone_number=self.tutor_phone_number)
        result = add_tutor(tutor)
        self.assertEqual(result, 0) 
    
    
    def test_update_students_from_excel(self):
        """
        Read information from received_xlsx/shedule_new.xlsx file,
        process and query the DB.
        Test passed if a list is returned, not None.
        """
        shedule = os.path.abspath("received_xlsx/shedule_new.xlsx")
        tutor = Tutor(chat_id=self.tutor_chat_id, full_name=self.tutor_full_name, phone_number=self.tutor_phone_number)
        results = update_students_from_excel(shedule, tutor)
        self.assertIsNotNone(results)


    def test_update_student_contact(self):
        """
        Try to insert contact information to a student in DB.
        Test passed if updating existing user returns 1 and non-existing user returns 0.
        """

        result = update_student_contact(self.student_unique_id, 235234234, '823942235232')
        self.assertEqual(result, 1)


        # Store the current log level to restore it later
        original_log_level = logging.getLogger().getEffectiveLevel()
        # Set the log level to a higher level, e.g., WARNING or CRITICAL
        logging.disable(logging.CRITICAL)
        try:
            result = update_student_contact('not_exists', 235234234, '823942235232')
        except Exception as exp:
            logger.exception(exp)
        # Restore the original log level after the tests
        logging.disable(original_log_level)

        self.assertEqual(result, 0)
        

    def test_remove_outdated_students(self):
        """
        Delete records of all students from DB except of given ID list
        Test passed if amount of records is equal to the length of test list
        """
        tutor = Tutor(tutor_id = self.tutor_id, chat_id=self.tutor_chat_id, full_name=self.tutor_full_name, phone_number=self.tutor_phone_number)
        students = [Student(student_id=3, unique_id=self.student_unique_id, full_name=self.student_full_name, tutor=tutor)]
        remove_outdated_students(students)
        students_read_query = f"SELECT * FROM student;"
        students_db = execute_query(students_read_query)
        self.assertEqual(len(students_db), len(students))


    def test_get_student_payment(self):
        """
        Read student's payment information
        """
        chat_id = self.student_chat_id
        am, cur = get_student_payment(tg_chat_id=chat_id)
        self.assertEqual(am, self.payment_amount)
        self.assertEqual(cur, self.payment_currency)


    def test_get_set_chat_state(self):
        """
        Sets chat state, then reads it back from DB
        Test passed if values match
        """
        id = 777
        test_state = "TEST"
        set_chat_state(tg_chat_id=id, state=test_state)
        db_state = get_chat_state(tg_chat_id=id)
        self.assertEqual(test_state[0], db_state[0])


if __name__ == '__main__':
    unittest.main()