import inflection
import re

from chartparse.exceptions import RegexFatalNotMatchError
from chartparse.util import DictPropertiesEqMixin


class Properties(DictPropertiesEqMixin):
    # Known fields in the [Song] section and the functions that should be used
    # to process them.
    _field_transformers = {
            "Name": str,
            "Artist": str,
            "Charter": str,
            "Album": str,
            "Year": str,
            "Offset": int,
            "Resolution": int,
            "Player2": str,
            "Difficulty": int,
            "PreviewStart": int,
            "PreviewEnd": int,
            "Genre": str,
            "MediaType": str,
            "MusicStream": str}

    _regex = r"^\s*?([A-Za-z0-9]+?)\s=\s\"?(.*?)\"?\s*?$"
    _regex_prog = re.compile(_regex)

    def __init__(self, injections):
        for field_name, value in injections.items():
            setattr(self, field_name, value)

    @classmethod
    def from_chart_lines(cls, lines):
        injections = dict()
        for line in lines:
            m = cls._regex_prog.match(line)
            if not m:
                raise RegexFatalNotMatchError(cls._regex, line)
            field_name, raw_value = m.group(1), m.group(2)
            if field_name in cls._field_transformers:
                transformed_value = cls._field_transformers[field_name](raw_value)
                value_to_set = transformed_value
            else:
                # TODO: Log that transformer couldn't be found.
                value_to_set = raw_value
            pythonic_field_name = inflection.underscore(field_name)
            injections[pythonic_field_name] = value_to_set
        return cls(injections)

    def __repr__(self):  # pragma: no cover
        return str(self.__dict__)
