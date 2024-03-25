import os
import sys
import unittest
import logging
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.adapters.db_connector import execute_query
from app.common.utils import add_tutor, update_students_from_excel, update_student_contact
from app.common.models import Tutor, Student


class TestXlsParser(unittest.TestCase):
    logger = logging.getLogger(__name__)
    logging.basicConfig(format = '%(asctime)s %(module)s %(levelname)s: %(message)s',
                    datefmt = '%m/%d/%Y %H:%M:%S', level = logging.INFO)

    def setUp(self) -> None:
        self.tutor_contact_id = 252353213
        self.tutor_full_name = 'Tutor 2'
        self.tutor_phone_number = '23423523522'
        self.student_unique_id = 'Student_1'
        self.student_full_name = 'Student 1'
        tutor_write_query = "INSERT INTO tutor(tutor_id, contact_id, full_name, phone_number, added_at) VALUES (" + \
            str(3) + ", " + \
            str(self.tutor_contact_id) + ", '" + \
            str(self.tutor_full_name) + "', '" + \
            str(self.tutor_phone_number) + "', '" + \
            str(datetime.now()) + "');"
        execute_query(tutor_write_query, readonly=True)
        tutor_read_query = f"SELECT tutor_id FROM tutor WHERE contact_id = {self.tutor_contact_id}"
        tutor_id = execute_query(tutor_read_query)
        student_write_query = "INSERT INTO student(student_id, tutor_id, unique_id, full_name, added_at) VALUES (" + \
            str(3) + ", " + \
            str(tutor_id[0][0]) + ", '" + \
            str(self.student_unique_id) + "', '" + \
            str(self.student_full_name) + "', '" + \
            str(datetime.now()) + "');"
        execute_query(student_write_query, readonly=True)
        return super().setUp()


    def test_add_tutor(self):
        """
        Try to add a new tutor in DB.
        Test passed if adding new tutor returns 0 (it was already added in DB).
        """
        tutor = Tutor(contact_id=self.tutor_contact_id, full_name=self.tutor_full_name, phone_number=self.tutor_phone_number)
        result = add_tutor(tutor)
        self.assertEqual(result, 0) 
    
    
    def test_students_read(self):
        """
        Read information from received_xlsx/shedule_new.xlsx file,
        process and query the DB.
        Test passed if a list is returned, not None.
        """
        shedule = os.path.abspath("received_xlsx/shedule_new.xlsx")
        tutor = Tutor(contact_id=self.tutor_contact_id, full_name=self.tutor_full_name, phone_number=self.tutor_phone_number)
        results = update_students_from_excel(shedule, tutor)
        self.assertIsNotNone(results)


    def test_students_update(self):
        """
        Try to insert contact information to a student in DB.
        Test passed if updating existing user returns 1 and non-existing user returns 0.
        """

        result = update_student_contact(self.student_unique_id, 235234234, '823942235232')
        self.assertEqual(result, 1)

        result = update_student_contact('not_exists', 235234234, '823942235232')
        self.assertEqual(result, 0)
        

if __name__ == '__main__':
    unittest.main()