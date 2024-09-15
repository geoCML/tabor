from tabor_layer import TaborLayer


class FeatureGroup(object):
    def __init__(self, name: str) -> None:
        self.name = name
        self.schema = ""
        self.owner = ""
        self.layers = []


    def add_layer(self, layer: TaborLayer) -> list[TaborLayer]:
        if not layer.get_pk_field()[0]:
            raise Exception(f"{layer.name} has no primary key but it is in group {self.name}")

        if not self.schema:
            self.schema = layer.schema

        if not self.owner:
            self.owner = layer.owner

        if layer.schema != self.schema:
            raise Exception(f"{layer.name} is in the wrong schema, expected {self.schema} but got {layer.schema}")

        if layer.owner != self.owner:
            raise Exception(f"{layer.name} has the wrong owner, expected {self.owner} but got {layer.owner}")

        self.layers.append(layer)
        return self.layers


    def gather_foreign_keys(self) -> str:
        foreign_keys = []

        for layer in self.layers:
            pk_name, pk_type = layer.get_pk_field()
            foreign_keys.append(f"""{layer.name}__fgid {pk_type} references "{layer.schema}"."{layer.name}"({pk_name})""")
        return f"({", ".join(foreign_keys)})"


    def __str__(self) -> str:
        return f"""CREATE TABLE IF NOT EXISTS "{self.schema}"."{self.name}" {self.gather_foreign_keys()}; """
