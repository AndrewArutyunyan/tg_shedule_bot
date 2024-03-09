import os
import sys
import unittest
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.adapters.xls_parser import get_students


class TestXlsParser(unittest.TestCase):
    logger = logging.getLogger(__name__)
    logging.basicConfig(format = '%(asctime)s %(module)s %(levelname)s: %(message)s',
                    datefmt = '%m/%d/%Y %H:%M:%S', level = logging.INFO)

    def test_xlsx_read(self):
        """
        Read the shedule_new.xlsx and extract the list of students.
        Test if number of students if more then 0
        """
        shedule = os.path.abspath("received_xlsx/shedule_new.xlsx")
        s = get_students(shedule)
        logging.info(f"Successfully read {len(s)} lines from the Excel table")
        self.assertGreater(len(s), 0)


if __name__ == '__main__':
    unittest.main()
