from enum import Enum


class RequestStatusEnum(str, Enum):
    PENDING = "ожидание"
    APPROVED = "подвержден"
    REJECTED = "отвергнут"
