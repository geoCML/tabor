import re
from yaml import safe_dump, safe_load

from constraint import Constraint, Trigger
from feature_group import FeatureGroup
from tabor_layer import TaborLayer
from consts import VERSION


class TaborFile(object):
    # TODO: Use hashmaps!
    groups: list[FeatureGroup] = []
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

                        constraints: list[dict] = []
                        try:
                            constraints: list[dict] = layer["constraints"]
                        except KeyError:
                            pass


                        group = ""
                        try:
                            group = layer["group"]
                        except KeyError:
                            pass

                        self.add_layer(layer["name"], layer["schema"], geometry, layer["owner"], layer["fields"], constraints, group)

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

                derived_constraints: list[dict] = []
                try:
                    for trigger in values["constraints"]:
                        derived_constraints.append(Trigger(trigger).constraint.constraint)
                except KeyError:
                    pass

                derived_group = None
                try:
                    derived_group = values["group"]
                except KeyError:
                    pass
                self.add_layer(table.split(".")[1], table.split(".")[0], geom, values["owner"], values["fields"], derived_constraints, derived_group)


    def add_layer(self, name: str, schema: str, geometry: str | None, owner: str, fields: dict, constraints: list[dict], group: str | None) -> TaborLayer:
        layer = TaborLayer(name, schema, geometry, owner, fields, constraints, group)
        if group:
            feature_group = self.add_or_get_group(group)
            feature_group.add_layer(layer)
        self.layers.append(layer)
        return self.layers[len(self.layers) - 1]


    def add_or_get_group(self, name: str) -> FeatureGroup:
        for group in self.groups:
            if group.name == name:
                return group

        self.groups.append(FeatureGroup(name))
        return self.groups[len(self.groups) - 1]


    def to_psql(self) -> dict:
        result = {}
        result["layers"] = {}
        for layer in self.layers:
            result["layers"][layer.name] = {}
            fields = []
            for field in layer.fields:
                fields.append(field.as_psql())

            if layer.get_pk_field()[0]:
                pk_query = f""", PRIMARY KEY ({layer.get_pk_field()[0]})"""
            else:
                pk_query = ""

            if layer.geometry:
                geom_query = """, geom geometry"""
            else:
                geom_query = ""

            result["layers"][layer.name]["schema"] = f"""CREATE TABLE IF NOT EXISTS "{layer.schema}"."{layer.name}" ({", ".join(fields)}{geom_query}{pk_query});"""
            result["layers"][layer.name]["owner"] = f"""ALTER TABLE "{layer.schema}"."{layer.name}" OWNER TO {layer.owner};"""

            result["layers"][layer.name]["constraints"] = []
            for constraint in layer.constraints:
                result["layers"][layer.name]["constraints"].append(str(constraint))

            if layer.geometry:
                result["layers"][layer.name]["geometry"] = f"""ALTER TABLE "{layer.schema}"."{layer.name}" ALTER COLUMN geom TYPE Geometry({layer.derive_geometry_type()});"""

        result["groups"] = {}
        for group in self.groups:
            result["groups"][group.name] = {}
            result["groups"][group.name]["schema"] = str(group)
            result["groups"][group.name]["owner"] = f"""ALTER TABLE "{group.schema}"."{group.name}" OWNER TO {group.owner};"""

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
