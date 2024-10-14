class TaborFieldType(object):
    postgres_integer_types = ("smallint", "integer", "bigint", "int2", "int4", "int8")
    postgres_numerical_types = ("double precision", "float", "numeric")
    postgres_text_types = ("character varying", "name", "text")
    postgres_binary_types = ("boolean")
    postgres_collection_types = ("TEXT ARRAY", "text array")  # TODO: https://github.com/geoCML/tabor/issues/27
    postgres_generic_types = ("USER-DEFINED", "user-defined")  # TODO: https://github.com/geoCML/tabor/issues/26

    def __init__(self, type: str):
        self.valid_types = ("text", "int", "numeric", "boolean", "text array", "user-defined")
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
            return type.lower()

        if type in self.postgres_generic_types:
            return "user-defined"

        return type


    def set_type(self, type: str):
        type = self.convert_postgres_type_to_tabor_field_type(type)

        if type not in self.valid_types:
            raise Exception(f"Literal '{type}' is not a valid field type. Valid field types are {self.valid_types}")

        self.type = type


    def __str__(self) -> str:
        return self.type
