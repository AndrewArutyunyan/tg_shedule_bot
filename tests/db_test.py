import os
import sys
import unittest
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.adapters.db import load_config, execute_query


class TestXlsParser(unittest.TestCase):
    logger = logging.getLogger(__name__)
    logging.basicConfig(format = '%(asctime)s %(module)s %(levelname)s: %(message)s',
                    datefmt = '%m/%d/%Y %H:%M:%S', level = logging.INFO)

    def test_sql_connection(self):
        """
        Query the database from database.ini file.
        Test connection.
        """
        conf_file = 'config/database.ini'
        config = load_config(conf_file)
        results = execute_query("SELECT 1;", config=config, writeonly=False)
        self.assertEqual(results, [(1,)])

    def test_sql_table_query(self):
        """
        Query the database from database.ini file and fetch all records from students table.
        Test if query will not fail
        """
        results = execute_query("SELECT * from student;")
        if results is not None:
            logging.info(f"Successfully read {len(results)} lines from the DB table student")
        self.assertIsNotNone(results, "SQL Read returned None")

if __name__ == '__main__':
    unittest.main()