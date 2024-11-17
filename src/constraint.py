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
        return f"""CREATE OR REPLACE FUNCTION {self.layer}___on___{other_layer}() RETURNS trigger AS $$ DECLARE overlap boolean; BEGIN SELECT Count(*) INTO overlap FROM {other_layer} WHERE ST_Covers({other_layer}.geom, NEW.geom); IF NOT overlap THEN RAISE EXCEPTION '{self.layer} is not on {other_layer}'; END IF; RETURN NEW; END; $$ LANGUAGE 'plpgsql'; CREATE CONSTRAINT TRIGGER {self.layer}___on___{other_layer} AFTER INSERT OR UPDATE ON {self.layer} FOR EACH ROW EXECUTE FUNCTION {self.layer}___on___{other_layer}();"""


    def length(self, maximum: float | None, minimum: float | None):
        if not maximum:
            maximum = 99999999999

        if not minimum:
            minimum = 0

        return f"""CREATE OR REPLACE FUNCTION {self.layer}___length___{str(minimum).replace(".", "d")}_{str(maximum).replace(".", "d")}() RETURNS trigger AS $$ DECLARE length numeric; BEGIN SELECT ST_LENGTH(NEW.geom::geography) INTO length; IF length > {maximum} THEN RAISE EXCEPTION '{self.layer} is longer than {maximum}'; ELSE IF length < {minimum} THEN RAISE EXCEPTION '{self.layer} is shorter than {minimum}'; END IF; END IF; RETURN NEW; END; $$ LANGUAGE 'plpgsql'; CREATE CONSTRAINT TRIGGER {self.layer}___length___{str(minimum).replace(".", "d")}_{str(maximum).replace(".", "d")} AFTER INSERT OR UPDATE ON {self.layer} FOR EACH ROW EXECUTE FUNCTION {self.layer}___length___{str(minimum).replace(".", "d")}_{str(maximum).replace(".", "d")}();"""


    def as_dict(self) -> dict:
        return self.constraint


    def __str__(self) -> str:
        if self.constraint_type.type == "on":
            try:
                layer = self.constraint["layer"]
            except KeyError:
                raise Exception("Constraint 'on' needs a relative layer value")
            return self.on(layer)

        if self.constraint_type.type == "length":
            maximum = None
            minimum = None

            if "maximum" in self.constraint:
                maximum = self.constraint["maximum"]
                try:
                    float(maximum)
                except ValueError:
                    raise Exception(f"Value '{maximum}' is not a numeric value")

            if "minimum" in self.constraint:
                minimum = self.constraint["minimum"]
                try:
                    float(minimum)
                except ValueError:
                    raise Exception(f"Value '{minimum}' is not a numeric value")

            if not minimum and not maximum:
                raise Exception("Constraint 'length' needs a minimum or maximum value")

            return self.length(maximum, minimum)

        return ""


class Trigger(object):
    """
    Triggers are strings that can be used to derive Constraints

    e.g. trees_on_grass -> { "name": "on", "layer": "grass" }
    """
    def __init__(self, name: str) -> None:
        self.constraint = self.derive_constraint_from_name(name)


    def derive_constraint_from_name(self, name) -> Constraint:
        if "___on___" in name:
            return Constraint({
                "name": "on",
                "layer": name.split("___on___")[1]
            }, name.split("___on___")[0])
        elif "___length___" in name:
            return Constraint({
                "name": "length",
                "minimum": float(name.split("___length___")[1].split("_")[0].replace("d", ".")),
                "maximum": float(name.split("___length___")[1].split("_")[1].replace("d", "."))
            }, name.split("___length___")[0])

        raise Exception(f"Cannot derive a constraint from trigger '{name}'")

