from tabor_constraint_type import TaborConstraintType


class Constraint(object):
    def __init__(self, constraint: dict, layer: str) -> None:
        self.constraint = constraint
        self.layer = layer

        try:
            if self.constraint["name"] == True:
                self.constraint["name"] = "on"
            self.constraint_type = TaborConstraintType(self.constraint["name"])
        except KeyError:
            raise Exception(f"Constraint has no name")


    def on(self, other_layer: str) -> str:
        return f"""CREATE OR REPLACE FUNCTION {self.layer}_on_{other_layer}() RETURNS trigger AS $$ DECLARE overlap boolean; BEGIN SELECT Count(*) INTO overlap FROM {other_layer} WHERE ST_Contains({other_layer}.geom, NEW.geom); IF NOT overlap THEN RAISE EXCEPTION '{self.layer} is not on {other_layer}'; END IF; RETURN NEW; END; $$ LANGUAGE 'plpgsql'; CREATE CONSTRAINT TRIGGER {self.layer}_on_{other_layer} AFTER INSERT OR UPDATE ON {self.layer} FOR EACH ROW EXECUTE FUNCTION {self.layer}_on_{other_layer}();"""


    def as_dict(self) -> dict:
        return self.constraint


    def __str__(self) -> str:
        if self.constraint_type.type == "on":
            try:
                layer = self.constraint["layer"]
            except KeyError:
                raise Exception("Constraint 'on' needs a relative layer value")
            return self.on(layer)
        return ""


class Trigger(object):
    """
    Triggers are strings that can be used to derive Constraints

    e.g. trees_on_grass -> { "name": "on", "layer": "grass" }
    """
    def __init__(self, name: str) -> None:
        self.constraint = self.derive_constraint_from_name(name)


    def derive_constraint_from_name(self, name) -> Constraint:
        if "_on_" in name:
            return Constraint({
                "name": "on",
                "layer": name.split("_on_")[1]
            }, name.split("_on_")[0])

        raise Exception(f"Cannot derive a constraint from trigger '{name}'")
