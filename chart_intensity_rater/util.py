from enum import Enum


class AllValuesGettableEnum(Enum):
    @classmethod
    def all_values(cls):
        return tuple(map(lambda c: c.value, cls))
