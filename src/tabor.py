from argparse import ArgumentParser

from tabor_file import TaborFile
from db_connector import DBConnector

import sys

from consts import VERSION

sys.tracebacklimit = -1


def read(file_path: str) -> None:
    try:
        tabor_src = TaborFile(file_path)
    except Exception as e:
        raise Exception("Failed to read .tabor file")

    print(tabor_src.to_psql())


def write(file_path: str, db: str, username: str, password: str, host: str, port: str) -> None:
    try:
        data = {}
        db_connector = DBConnector(db, username, password, host, port)
        tables = db_connector.get_tables()

        for table in tables:
            schema = table.split(".")[0]
            table_name = table.split(".")[1]

            data[table] = {}
            data[table]["fields"] = db_connector.get_fields_for_table(schema, table_name)
            data[table]["constraints"] = db_connector.get_triggers_for_table(table_name)

            geom_type = db_connector.get_geometry_type_for_table(schema, table_name)
            if geom_type:
                data[table]["geometry"] = geom_type

            data[table]["owner"] = username

        tabor_src = TaborFile(file_path, psql_data=data)
        tabor_src.write()
        print(f"Wrote .tabor file to {file_path}")
    except:
        raise Exception("Failed to write PostGIS database to a .tabor file")


if __name__ == "__main__":
    parser = ArgumentParser(description='tabor <command> <flags>')
    parser.add_argument('command', help='`read`: Converts a .tabor file into a PostGIS schema query.\n' +
                                        '`write`: Converts a PostGIS database into a .tabor file.\n' +
                                        '`version`: Show the current installed version of Tabor.\n')
    parser.add_argument('--file', help='The path to the .tabor file.')
    parser.add_argument('--db', help='The name of the PostGIS database to connect to.')
    parser.add_argument('--username', help='The username of a database user.')
    parser.add_argument('--password', help='The password of a database user.', default=None)
    parser.add_argument('--host', help='The hostname of the PostGIS database to connect to.', default="localhost")
    parser.add_argument('--port', help='The port of the PostGIS database to connect to.', default=5432)

    args = parser.parse_args()

    if args.command == "read":
        if not args.file:
            raise Exception("You must provide one file to read from (--file)")
        read(args.file)
    elif args.command == "write":
        if not args.file:
            raise Exception("You must provide one file to write to (--file)")

        if not args.db:
            raise Exception("You must provide a PostGIS database to write to the .tabor file (--db)")

        if not args.username:
            raise Exception("You must provide a PostGIS database user to connect to your database (--username)")

        write(args.file, args.db, args.username, args.password, args.host, args.port)
    elif args.command == "version":
        print(VERSION)
    else:
        raise Exception(f"No idea what '{args.command}' is!")

    sys.exit(0)
