import xlwings as xw
from ..common.models import Student
from typing import List


def get_students(book:str)->List:
    sheet = xw.Book(book).sheets['Current_month']
    students = []
    i = 42
    while student_id := sheet[f"N{i}"].value:
        student_name = sheet[f"N{i}"].value
        students.append(Student(student_id=student_id, name=student_name))
        i += 1
    
    return students


if __name__ == "__main__":
    shedule = "received_xlsx/shedule_new.xlsx"
    s = get_students(shedule)