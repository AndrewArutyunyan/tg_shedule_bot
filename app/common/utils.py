from typing import List

from ..adapters.xls_parser import get_students
from ..adapters.db_connector import execute_query


def parse_students(filename:str)->List:
    """
    Extract students information from the Excel file, 
    write to Database and return back the list.
    """
    students = get_students(filename)
    student_ids = [str(s.student_id) for s in students]
    read_query = "SELECT student_id FROM student WHERE student_id IN ('" + \
        "', '".join(student_ids) + \
        "');"
    print(read_query)
