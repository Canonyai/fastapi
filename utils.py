from enum import Enum, auto


class Content(Enum):
    ISSUE = auto()
    REPO = auto()
    PR = auto()
    FILE = auto()
    COMMIT = auto()


class Language(Enum):
    PY = auto()
    JS = auto()
    TYPED = auto()
    UNTYPED = auto()
