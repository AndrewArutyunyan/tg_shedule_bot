from attr import dataclass


@dataclass
class Tutor:
    tutor_id: int = None
    chat_id: int = None
    full_name: str = None
    phone_number: str = None


@dataclass
class Student:
    student_id:int = None
    chat_id: str = None
    unique_id: str = None
    full_name: str = None
    tutor: Tutor = None
    phone_number: str = None
    payment_amount: float = None
    payment_currency: float = None

