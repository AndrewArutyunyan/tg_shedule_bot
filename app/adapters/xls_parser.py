from openpyxl import load_workbook
from ..common.models import Student
from typing import List
import warnings


def read_students_excel(book:str)->List[Student]:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sheet = load_workbook(book, data_only=True)['Current_month']
    students = []
    i = 42
    while id := sheet[f"N{i}"].value:
        student_name = sheet[f"O{i}"].value
        students.append(Student(unique_id=id, full_name=student_name))
        i += 1
    
    return students
