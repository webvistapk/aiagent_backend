from enum import Enum

class DurationType(Enum):
    DAYS = 'days'
    MONTHS = 'months'
    YEARS = 'years'

class Role(Enum):
    ADMIN = 'admin'
    USER = 'user'