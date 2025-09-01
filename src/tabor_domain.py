import re
from tabor_field_type import TaborFieldType

class TaborDomain(object):
    values: tuple[any]

    def __init__(self, name: str, values: list[any], data_type: str):
        self.name = name
        self.values = tuple(values)
        self.type = TaborFieldType(data_type, data_type)

    def collect_constraint_values_from_psql(self, psql: str):
        match_pattern = r"(?:'([^']+)'|(\b\d+))(?:\s*::text)?"
        matches = re.findall(match_pattern, psql)
        self.values = [m[0] if m[0] else m[1] for m in matches]

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "type": f"{self.type}",
            "values": self.values,
        }

