from enum import Enum


class RequestStatusEnum(Enum):
    PENDING = "ожидание"
    APPROVED = "подвержден"
    REJECTED = "отвергнут"
