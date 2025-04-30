from enum import Enum


class EmailConfirmationTypeEnum(str, Enum):
    REGISTRATION = "registration"
    PASSWORD_RESET = "password_reset"
