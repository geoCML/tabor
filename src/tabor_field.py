from yaml import YAMLObject
from tabor_field_type import TaborFieldType


class TaborField(YAMLObject):
    def __init__(self, name: str, type: str, udt_name: str, pk: bool) -> None:
        super().__init__()

        self.name = name
        self.type = TaborFieldType(type, udt_name)
        self.pk = pk


    def as_psql(self) -> str:
        return f"\"{self.name}\" {self.type}"


    def as_dict(self) -> dict:
        var_dict = {
            "name": self.name,
            "type": str(self.type),
        }

        if self.pk:
            var_dict["pk"] = self.pk

        return var_dict
