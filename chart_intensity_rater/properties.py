import re

from chart_intensity_rater.util import DictPropertiesEqMixin


# TODO: Unit test this.
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

    def __init__(self, iterator_getter):
        for line in iterator_getter():
            m = self._regex_prog.match(line)
            if not m:
                raise ValueError(f"could not parse song property from line '{line}'")
            field_name, raw_value = m.group(1), m.group(2)
            if field_name in self._field_transformers:
                transformed_value = self._field_transformers[field_name](raw_value)
                value_to_set = transformed_value
            else:
                # TODO: Log that transformer couldn't be found.
                value_to_set = raw_value
            setattr(self, field_name, value_to_set)

    def __repr__(self):  # pragma: no cover
        return str(self.__dict__)
