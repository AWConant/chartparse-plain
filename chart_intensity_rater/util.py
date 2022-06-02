from enum import Enum


class AllValuesGettableEnum(Enum):
    @classmethod
    def all_values(cls):
        return tuple(map(lambda c: c.value, cls))


class DictPropertiesEqMixin(object):
    def __eq__(self, other):
        if not issubclass(other.__class__, DictPropertiesEqMixin):
            raise NotImplementedError
        return self.__dict__ == other.__dict__
