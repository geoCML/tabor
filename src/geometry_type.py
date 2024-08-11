class GeometryType(object):
    postgis_polyline_types = ("POLYLINE", "Polyline", "Linestring", "LINESTRING")
    postgis_polygon_types = ("POLYGON", "Polygon")
    postgis_point_types = ("POINT", "Point")
    postgis_multi_polygon_types = ("MULTIPOLYGON", "Multipolygon")
    postgis_geometry_generic_types = ("GEOMETRY", "Geometry")

    def __init__(self, type: str):
        self.valid_types = ("line", "multi polygon", "polygon", "point", "geometry")
        self.set_type(type)


    def convert_postgis_geometry_to_geometry_type(self, type):
        if type in self.postgis_polyline_types:
            return "line"

        if type in self.postgis_polygon_types:
            return "polygon"

        if type in self.postgis_point_types:
            return "point"

        if type in self.postgis_multi_polygon_types:
            return "multi polygon"

        if type in self.postgis_geometry_generic_types:
            return "geometry"

        return type

    def set_type(self, type: str):
        type = self.convert_postgis_geometry_to_geometry_type(type)
        if type not in self.valid_types:
            raise Exception(f"Literal '{type}' is not a valid geometry type. Valid geometry types are {self.valid_types}")

        self.type = type


    def __str__(self) -> str:
        return self.type
