from attr import dataclass


@dataclass
class Tutor:
    tutor_id: str
    name: str
    phone_number: str = None


@dataclass
class Student:
    student_id: str
    name: str
    tutor: Tutor = None
    phone_number: str = None

