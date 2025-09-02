class TaborFieldType(object):
    postgres_integer_types = ("smallint", "integer", "bigint", "int2", "int4", "int8")
    postgres_numerical_types = ("double precision", "float", "numeric", "float8")
    postgres_text_types = ("character varying", "name", "text")
    postgres_binary_types = ("boolean")
    postgres_collection_types = ("ARRAY", "array")
    postgres_generic_types = ("USER-DEFINED", "user-defined")  # TODO: https://github.com/geoCML/tabor/issues/26
    postgres_temporal_types = ("timestamp", "date", "time")

    def __init__(self, type: str, udt_name: str):
        self.valid_types = ("text", "int", "numeric", "boolean", "int array", "text array", "numeric array", "boolean array", "user-defined", "date", "time", "timestamp")
        self.udt_name = udt_name

        if self.udt_name == "" and len(type.split(" ")) > 1:
            self.udt_name = type.split(" ")[0]
            type = type.split(" ")[1]

        if type != "":
            self.set_type(type)


    def convert_postgres_type_to_tabor_field_type(self, type: str) -> str:
        if type in self.postgres_integer_types:
            return "int"

        if type in self.postgres_text_types:
            return "text"

        if type in self.postgres_numerical_types:
            return "numeric"

        if type in self.postgres_binary_types:
            return "boolean"

        if type in self.postgres_collection_types:
            if "_" in self.udt_name:
                fmt_udt_name = self.convert_postgres_type_to_tabor_field_type(self.udt_name.split("_")[1])
            else:
                fmt_udt_name = self.udt_name

            if fmt_udt_name not in self.valid_types:
                raise Exception(f"Literal '{fmt_udt_name}' is not a valid field type. Valid field types are {self.valid_types}")
            return f"{fmt_udt_name} {type.lower()}"

        if type in self.postgres_generic_types:
            return "user-defined"

        return type


    def set_type(self, type: str):
        type = self.convert_postgres_type_to_tabor_field_type(type)

        if type not in self.valid_types and type[0] != "_":
            raise Exception(f"Literal '{type}' is not a valid field type. Valid field types are {self.valid_types}")

        self.type = type


    def __str__(self) -> str:
        return self.type
