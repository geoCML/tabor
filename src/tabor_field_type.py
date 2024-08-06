class TaborFieldType(object):
    def __init__(self, type: str):
        self.valid_types = ("int8", "varchar", "double")
        self.set_type(type)


    def set_type(self, type: str):
        if type not in self.valid_types:
            raise Exception(f"Literal '{type}' is not a valid field type. Valid field types are {self.valid_types}")

        self.type = type


    def __str__(self) -> str:
        return self.type
