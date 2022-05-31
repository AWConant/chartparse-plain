from enum import Enum


class Superclass(object):
    def __init__(self, foo):
        self.foo = foo

class Subclass(Superclass):
    def __init__(self, foo, bar):
        super().__init__(foo)
        self.bar = bar

sp = Superclass(1)
sb = Subclass(3, 2)

class AllValuesGettableEnum(Enum):
    @classmethod
    def all_values(cls):
        return tuple(map(lambda c: c.value, cls))

class _Difficulty(AllValuesGettableEnum):
    EXPERT = "Expert"
    HARD = "Hard"
    MEDIUM = "Medium"
    EASY = "Easy"

print(tuple(_Difficulty))
print(_Difficulty.all_values())

print(_Difficulty("Expert"))

class _Note(Enum):
    OPEN                         = bytearray((0, 0, 0, 0, 0))
    GREEN                        = bytearray((1, 0, 0, 0, 0))
    GREEN_RED                    = bytearray((1, 1, 0, 0, 0))
    GREEN_YELLOW                 = bytearray((1, 0, 1, 0, 0))
    GREEN_BLUE                   = bytearray((1, 0, 0, 1, 0))
    GREEN_ORANGE                 = bytearray((1, 0, 0, 0, 1))
    GREEN_RED_YELLOW             = bytearray((1, 1, 1, 0, 0))
    GREEN_RED_BLUE               = bytearray((1, 1, 0, 1, 0))
    GREEN_RED_ORANGE             = bytearray((1, 1, 0, 0, 1))
    GREEN_YELLOW_BLUE            = bytearray((1, 0, 1, 1, 0))
    GREEN_YELLOW_ORANGE          = bytearray((1, 0, 1, 0, 1))
    GREEN_BLUE_ORANGE            = bytearray((1, 0, 0, 1, 1))
    GREEN_RED_YELLOW_BLUE        = bytearray((1, 1, 1, 1, 0))
    GREEN_RED_YELLOW_ORANGE      = bytearray((1, 1, 1, 0, 1))
    GREEN_RED_BLUE_ORANGE        = bytearray((1, 1, 0, 1, 1))
    GREEN_YELLOW_BLUE_ORANGE     = bytearray((1, 0, 1, 1, 1))
    GREEN_RED_YELLOW_BLUE_ORANGE = bytearray((1, 1, 1, 1, 1))
    RED                          = bytearray((0, 1, 0, 0, 0))
    RED_YELLOW                   = bytearray((0, 1, 1, 0, 0))
    RED_BLUE                     = bytearray((0, 1, 0, 1, 0))
    RED_ORANGE                   = bytearray((0, 1, 0, 0, 1))
    RED_YELLOW_BLUE              = bytearray((0, 1, 1, 1, 0))
    RED_YELLOW_ORANGE            = bytearray((0, 1, 1, 0, 1))
    RED_BLUE_ORANGE              = bytearray((0, 1, 0, 1, 1))
    RED_YELLOW_BLUE_ORANGE       = bytearray((0, 1, 1, 1, 1))
    YELLOW                       = bytearray((0, 0, 1, 0, 0))
    YELLOW_BLUE                  = bytearray((0, 0, 1, 1, 0))
    YELLOW_ORANGE                = bytearray((0, 0, 1, 0, 1))
    YELLOW_BLUE_ORANGE           = bytearray((0, 0, 1, 1, 1))
    BLUE                         = bytearray((0, 0, 0, 1, 0))
    BLUE_ORANGE                  = bytearray((0, 0, 0, 1, 1))
    ORANGE                       = bytearray((0, 0, 0, 0, 1))


