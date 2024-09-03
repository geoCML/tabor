import re
from yaml import safe_dump, safe_load

from tabor_layer import TaborLayer
from consts import VERSION


class TaborFile(object):
    layers: list[TaborLayer] = []

    def __init__(self, path: str, psql_data: dict | None = None) -> None:
        self.path = path

        if not psql_data:
            try:
                with open(self.path, "r") as src:
                    yml = safe_load(src)
                    if yml["tabor"] != VERSION:
                        raise Exception(f"Your .tabor file uses version {yml["tabor"]}, which is out of date with the current version {VERSION}")

                    for layer in yml["layers"]:
                        try:
                            geometry = layer["geometry"]
                        except KeyError:
                            geometry = None

                        constraints: dict = {}
                        try:
                            constraints = layer["constraints"]
                        except KeyError:
                            pass

                        self.add_layer(layer["name"], layer["schema"], geometry, layer["owner"], layer["fields"], constraints)

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


                constraints: dict = {}
                try:
                    constraints = values["constraints"]
                except KeyError:
                    pass

                self.add_layer(table.split(".")[1], table.split(".")[0], geom, values["owner"], values["fields"], constraints)


    def add_layer(self, name: str, schema: str, geometry: str | None, owner: str, fields: dict, constraints: dict) -> TaborLayer:
        self.layers.append(TaborLayer(name, schema, geometry, owner, fields, constraints))
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

            result[layer.name]["constraints"] = []
            for constraint in layer.constraints:
                result[layer.name]["constraints"].append(str(constraint))

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
            "tabor": VERSION,
            "layers": layers_as_dict
        }
