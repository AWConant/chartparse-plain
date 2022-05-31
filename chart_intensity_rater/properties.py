import re


class Properties(object):
    # Known fields in the [Song] section and the functions that should be used
    # to process them.
    field_transformers = {
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

    field_regex_prog = re.compile(r"^\s*?([A-Za-z0-9]+?)\s=\s\"?(.*?)\"?\s*?$")

    def __init__(self, iterator_getter):
        for line in iterator_getter():
            m = self.field_regex_prog.match(line)
            if not m:
                raise ValueError(f"could not parse song property from line '{line}'")
            field_name, raw_value = m.group(1), m.group(2)
            if field_name in self.field_transformers:
                transformed_value = self.field_transformers[field_name](raw_value)
                value_to_set = transformed_value
            else:
                # TODO: Log that transformer couldn't be found.
                value_to_set = raw_value
            setattr(self, field_name, value_to_set)

    def __repr__(self):
        return str(self.__dict__)
