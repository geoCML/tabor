from geometry_type import GeometryType
from constraint import Constraint
from tabor_field_type import TaborFieldType
from tabor_field import TaborField


class TaborLayer(object):
    def __init__(self, name: str, schema: str, geometry: str | None, owner: str, fields: dict, constraints: list[dict], group: str | None) -> None:
        self.name = name
        self.schema = schema

        if geometry:
            self.geometry = GeometryType(geometry)
        else:
            self.geometry = None

        if group:
            self.group = group
        else:
            self.group = None

        self.constraints: list[Constraint] = []
        if constraints:
            for constraint in constraints:
                self.constraints.append(Constraint(constraint, self.name))

        self.owner = owner
        self.fields: list[TaborField] = []

        try:
            for field in fields:
                try:
                    pk = field["pk"]
                except KeyError:
                    pk = False

                try:
                    udt_name = field["udt_name"]
                except KeyError:
                    udt_name = ""

                self.add_field(field["name"], field["type"], udt_name, pk)
        except KeyError as e:
            raise Exception(f"Missing attribute in layer '{self.name}': {str(e)}")


    def add_field(self, name: str, type: str, udt_name: str, pk: bool) -> None:
        self.fields.append(TaborField(name, type, udt_name, pk))


    def get_pk_field(self) -> tuple[str, TaborFieldType]:
        for field in self.fields:
            if field.pk:
                return (field.name, field.type)
        return ("", TaborFieldType("", ""))


    def as_dict(self) -> dict:
        var_dict = {
            "name": self.name,
            "schema": self.schema,
            "owner": self.owner,
            "fields": [field.as_dict() for field in self.fields],
        }

        if self.constraints:
            var_dict["constraints"] = [constraint.as_dict() for constraint in self.constraints]

        if self.geometry:
            var_dict["geometry"] = str(self.geometry)

        if self.group:
            var_dict["group"] = self.group

        return var_dict


    def derive_geometry_type(self) -> str:
        if not self.geometry:
            return ""

        postgis_geometry_types = {
            "polyline": "Linestring",
            "point": "Point",
            "polygon": "Polygon",
            "multi polygon": "Multipolygon"
        }
        return postgis_geometry_types[self.geometry.type]


    def __str__(self) -> str:
        return f"{self.schema}.{self.name}"
