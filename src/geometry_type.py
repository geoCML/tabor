class GeometryType(object):
    def __init__(self, type: str):
        self.valid_types = ("polyline", "polygon", "point")
        self.set_type(type)


    def set_type(self, type: str):
        if type not in self.valid_types:
            raise Exception(f"Literal '{type}' is not a valid geometry type. Valid geometry types are {self.valid_types}")

        self.type = type


    def __str__(self) -> str:
        return self.type