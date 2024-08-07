import re
from yaml import safe_dump, safe_load

from src.tabor_layer import TaborLayer


class TaborFile(object):
    tabor = "0.1.0"  # Version number
    layers: list[TaborLayer] = []

    def __init__(self, path: str, psql_data: dict | None = None) -> None:
        self.path = path

        if not psql_data:
            try:
                with open(self.path, "r") as src:
                    yml = safe_load(src)
                    if yml["tabor"] != self.tabor:
                        raise Exception(f"Your .tabor file uses version {yml["tabor"]}, which is out of date with the current version {self.tabor}")

                    for layer in yml["layers"]:
                        try:
                            geometry = layer["geometry"]
                        except KeyError:
                            geometry = None

                        self.add_layer(layer["name"], layer["schema"], geometry, layer["owner"], layer["fields"])

            except FileNotFoundError:
                raise Exception(f"Failed to read .tabor file at {self.path}, does that path exist?")
            except KeyError as e:
                raise Exception(f"Missing attribute in .tabor file: {str(e)}")
        else:
            for table, values  in psql_data.items():
                try:
                    geom = values["geometry"]
                except KeyError:
                    geom = None

                self.add_layer(table.split(".")[1], table.split(".")[0], geom, owner=values["owner"], fields=values["fields"])


    def add_layer(self, name: str, schema: str, geometry: str | None, owner: str, fields: dict) -> TaborLayer:
        self.layers.append(TaborLayer(name, schema, geometry, owner, fields))
        return self.layers[len(self.layers) - 1]


    def to_psql(self) -> dict:
        result = {}
        for layer in self.layers:
            result[layer.name] = {}
            fields = []
            for field in layer.fields:
                fields.append(field.as_psql())

            if layer.get_pk_field():
                pk_query = f""", PRIMARY KEY ({layer.get_pk_field()})"""
            else:
                pk_query = ""

            if layer.geometry:
                geom_query = """, geom geometry"""
            else:
                geom_query = ""

            result[layer.name]["schema"] = f"""CREATE TABLE IF NOT EXISTS "{layer.schema}"."{layer.name}" ({", ".join(fields)}{geom_query}{pk_query});"""
            result[layer.name]["owner"] = f"""ALTER TABLE "{layer.schema}"."{layer.name}" OWNER TO {layer.owner};"""

            if layer.geometry:
                result[layer.name]["geometry"] = f"""ALTER TABLE "{layer.schema}"."{layer.name}" ALTER COLUMN geom TYPE Geometry({layer.derive_geometry_type()});"""

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
