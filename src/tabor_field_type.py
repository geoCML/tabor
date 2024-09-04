class TaborFieldType(object):
    postgres_integer_types = ("smallint", "integer", "bigint", "int2", "int4", "int8")
    postgres_numerical_types = ("double precision", "float", "numeric")
    postgres_text_types = ("character varying", "name", "text")

    def __init__(self, type: str):
        self.valid_types = ("text", "int", "numeric")
        self.set_type(type)


    def convert_postgres_type_to_tabor_field_type(self, type):
        if type in self.postgres_integer_types:
            return "int"

        if type in self.postgres_text_types:
            return "text"

        if type in self.postgres_numerical_types:
            return "numeric"

        return type


    def set_type(self, type: str):
        type = self.convert_postgres_type_to_tabor_field_type(type)

        if type not in self.valid_types:
            raise Exception(f"Literal '{type}' is not a valid field type. Valid field types are {self.valid_types}")

        self.type = type


    def __str__(self) -> str:
        return self.type
