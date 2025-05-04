from enum import Enum


class UserTypeEnum(str, Enum):
    CLIENT = "клиент"
    PSYCHOLOGIST = "психолог"
