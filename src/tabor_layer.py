from geometry_type import GeometryType
from constraint import Constraint
from tabor_field import TaborField


class TaborLayer(object):
    def __init__(self, name: str, schema: str, geometry: str | None, owner: str, fields: dict, constraints: list[dict]) -> None:
        self.name = name
        self.schema = schema

        if geometry:
            self.geometry = GeometryType(geometry)
        else:
            self.geometry = None

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

                self.add_field(field["name"], field["type"], pk)
        except KeyError as e:
            raise Exception(f"Missing attribute in layer '{self.name}': {str(e)}")


    def add_field(self, name: str, type: str, pk: bool) -> None:
        self.fields.append(TaborField(name, type, pk))


    def get_pk_field(self) -> str:
        for field in self.fields:
            if field.pk:
                return field.name
        return ""


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
