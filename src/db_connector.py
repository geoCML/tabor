from os import curdir
import psycopg2


class DBConnector(object):
    def __init__(self, db: str, username: str, password: str, host: str, port: str) -> None:
        try:
            self.connection = psycopg2.connect(dbname=db, user=username, password=password, host=host, port=port)
            self.cursor = self.connection.cursor()
        except:
            raise Exception(f"Failed to connect to {host}:{port} as '{username}'")


    def get_tables(self) -> list[str]:
        tables = []

        self.cursor.execute("""SELECT schema_name FROM information_schema.schemata WHERE schema_name != 'pg_catalog' AND schema_name != 'information_schema';""")
        schemata = self.cursor.fetchall()

        try:
            self.cursor.execute("""SELECT * FROM raster_columns;""")
            has_rasters = True
        except:
            has_rasters = False

        for schema in schemata:
            self.cursor.execute(f"""SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema[0]}'""")
            for table in self.cursor.fetchall():
                if has_rasters:
                    self.cursor.execute(f"""SELECT * FROM raster_columns WHERE r_table_name = '{table[0]}' AND r_table_schema = '{schema[0]}';""")
                    if self.cursor.fetchone():
                        continue
                tables.append(f"{schema[0]}.{table[0]}")

        return tables


    def get_groups(self) -> list[dict]:
        groups = []
        tables = self.get_tables()
        for table in tables:
            group = {}
            split_table = table.split(".")
            fields = self.get_fields_for_table(split_table[0], split_table[1])
            for field in fields:
                if "__fgid" in field["name"]:
                    try:
                        group[split_table[1]]
                    except KeyError:
                        group[split_table[1]] = {}
                        group[split_table[1]]["layers"] = []
                    group[split_table[1]]["layers"].append(field["name"].split("__fgid")[0])

            if group:
                groups.append(group)

        return groups



    def get_fields_for_table(self, schema: str, table: str) -> list[dict]:
        fields = []
        self.cursor.execute(f"""SELECT column_name, data_type, udt_name FROM information_schema.columns WHERE table_schema = '{schema}' AND table_name = '{table}' AND column_name != 'geom';""")

        for field, type, udt_name in self.cursor.fetchall():
            fields.append({
                "name": field,
                "type": type,
                "udt_name": udt_name,
                "pk": False
            })


        # Get pk fields
        self.cursor.execute(f"""SELECT column_name FROM information_schema.key_column_usage WHERE table_schema = '{schema}' AND table_name = '{table}';""")

        for field in self.cursor.fetchall():
            for compiled_field in fields:
                if compiled_field["name"] == field[0]:
                    tmp_field = compiled_field
                    fields.remove(compiled_field)
                    fields.append({
                        "name": field[0],
                        "type": tmp_field["type"],
                        "udt_name": tmp_field["udt_name"],
                        "pk": True
                    })
                    break
        return fields


    def get_geometry_type_for_table(self, schema: str, table: str) -> str:
        self.cursor.execute(f"""SELECT type FROM geometry_columns WHERE f_table_schema = '{schema}' AND f_table_name = '{table}' AND f_geometry_column = 'geom';""")
        result = self.cursor.fetchone()

        if not result:
            return ""

        return result[0]


    def get_triggers_for_table(self, table: str) -> set[str]:
        self.cursor.execute(f"""SELECT trigger_name FROM information_schema.triggers WHERE event_object_table = '{table}'""")
        return {trigger[0] for trigger in self.cursor.fetchall()}


    def execute_commit_query(self, query: str) -> None:
        self.cursor.execute(query)
        self.connection.commit()
