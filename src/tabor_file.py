import re
from yaml import safe_dump, safe_load

from src.tabor_layer import TaborLayer


class TaborFile(object):
    def __init__(self, path: str, psql: None | list[str] = None) -> None:
        self.path = path

        self.tabor = "0.1.0"  # Version number
        self.layers: list[TaborLayer] = []

        if not psql:
            try:
                with open(self.path, "r") as src:
                    yml = safe_load(src)
                    if yml["tabor"] != self.tabor:
                        raise Exception(f"Your .tabor file uses version {yml["tabor"]}, which is out of date with the current version {self.tabor}")

                    for layer in yml["layers"]:
                        self.add_layer(layer["name"], layer["schema"], layer["geometry"], layer["owner"], layer["fields"])

            except FileNotFoundError:
                raise Exception(f"Failed to read .tabor file at {self.path}, does that path exist?")
            except KeyError as e:
                raise Exception(f"Missing attribute in .tabor file: {str(e)}")
        else:
            for query in psql:
                layers = re.findall(fr"""CREATE TABLE IF NOT EXISTS "([a-zA-Z]+)"\."([a-zA-Z]+)" \((.*),+ PRIMARY KEY \((\S+)\)\);ALTER TABLE "[a-zA-Z]+"\."[a-zA-Z]+" OWNER TO (\S+);""", query)
                if not layers:
                    raise Exception(f"PostGIS query '{query}' is not valid")

                for layer in layers:
                    fields = []
                    for field in layer[2].split(", "):
                        field_dict = {}
                        attrs = field.split(" ")
                        field_dict["name"] = attrs[0]
                        field_dict["type"] = attrs[1]
                        field_dict["pk"] = False if attrs[0] != layer[3] else True
                        fields.append(field_dict)

                    self.add_layer(layer[1], layer[0], "polyline", layer[4], fields)  # TODO: infer the geometry type


    def add_layer(self, name: str, schema: str, geometry: str, owner: str, fields: dict) -> TaborLayer:
        self.layers.append(TaborLayer(name, schema, geometry, owner, fields))
        return self.layers[len(self.layers) - 1]


    def to_psql(self) -> dict:
        result = {}
        for layer in self.layers:
            result[layer.name] = {}
            fields = []
            for field in layer.fields:
                fields.append(field.as_psql())
            result[layer.name]["schema"] = f"""CREATE TABLE IF NOT EXISTS "{layer.schema}"."{layer.name}" ({", ".join(fields)}, geom geometry, PRIMARY KEY ({layer.get_pk_field()}));"""
            result[layer.name]["owner"] = f"""ALTER TABLE "{layer.schema}"."{layer.name}" OWNER TO {layer.owner};"""
            result[layer.name]["geometry"] = f"""ALTER TABLE "{layer.schema}."{layer.name}" ALTER COLUMN geom TYPE Geometry({layer.derive_geometry_type()});"""
        return result


    def write(self):
        yaml = safe_dump(self.as_dict(), sort_keys=False)
        try:
            with open(self.path, "w") as file:
                file.writelines(yaml)
        except FileNotFoundError:
            raise Exception(f"Failed to create .tabor file at {self.path}, does that path exist?")


    def as_dict(self) -> dict:
        layers_as_dict = []
        for layer in self.layers:
            layers_as_dict.append(layer.as_dict())

        return {
            "tabor": self.tabor,
            "layers": layers_as_dict
        }
