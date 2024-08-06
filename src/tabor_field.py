from yaml import YAMLObject
from src.tabor_field_type import TaborFieldType


class TaborField(YAMLObject):
    def __init__(self, name: str, type: str, pk: bool) -> None:
        super().__init__()

        self.name = name
        self.type = TaborFieldType(type)
        self.pk = pk


    def as_psql(self) -> str:
        return f"{self.name} {self.type}"


    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "type": str(self.type),
            "pk": self.pk
        }
