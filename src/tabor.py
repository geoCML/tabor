from argparse import ArgumentParser

from tabor_file import TaborFile
from db_connector import DBConnector

import sys
import json

from consts import VERSION

sys.tracebacklimit = -1


def load(file_path: str, db: str, username: str, password: str, host: str, port: str) -> None:
    db_connector = DBConnector(db, username, password, host, port)

    try:
        tabor_src = TaborFile(file_path)
        psql = tabor_src.to_psql()
        layers = psql["layers"]
        groups = psql["groups"]

        for _,layer in layers.items():
            for _,value in layer.items():
                if type(value) is list:
                    for query in value:
                        db_connector.execute_commit_query(query)
                else:
                    db_connector.execute_commit_query(value)

        for _,group in groups.items():
            for _,value in group.items():
                db_connector.execute_commit_query(value)

        print(f"Loaded {file_path} to {db}")
    except:
        db_connector.rollback()
        raise Exception("Failed to load .tabor file to PostGIS database")


def read(file_path: str) -> None:
    try:
        tabor_src = TaborFile(file_path)
    except:
        raise Exception("Failed to read .tabor file")

    print(tabor_src.to_psql())


def write(file_path: str, db: str, username: str, password: str, host: str, port: str, ignore_tables: list) -> None:
    db_connector = DBConnector(db, username, password, host, port)
    try:
        data = {}
        tables = db_connector.get_tables()
        groups = db_connector.get_groups()
        group_names = [list(group)[0] for group in groups]

        for table in tables:
            schema = table.split(".")[0]
            table_name = table.split(".")[1]

            if table_name in ignore_tables or table_name in group_names:
                continue

            data[table] = {}
            data[table]["fields"] = db_connector.get_fields_for_table(schema, table_name)
            data[table]["constraints"] = db_connector.get_triggers_for_table(table_name)

            geom_type = db_connector.get_geometry_type_for_table(schema, table_name)
            if geom_type:
                data[table]["geometry"] = geom_type
                srid = db_connector.get_srid_for_table(schema, table_name)
                if srid:
                    data[table]["srid"] = srid

            data[table]["owner"] = username

            for group in groups:
                for group_name,layers in group.items():
                    if table_name in layers["layers"]:
                        data[table]["group"] = group_name

        tabor_src = TaborFile(file_path, psql_data=data)
        tabor_src.write()
        print(f"Wrote .tabor file to {file_path}")
    except:
        db_connector.rollback()
        raise Exception("Failed to write PostGIS database to a .tabor file")


if __name__ == "__main__":
    parser = ArgumentParser(description='tabor <command> <flags>')
    parser.add_argument('command', help='`read`: Converts a .tabor file into a PostGIS schema query.\n' +
                                        '`write`: Converts a PostGIS database into a .tabor file.\n' +
                                        '`load`: Loads a PostGIS database from a .tabor file.\n' +
                                        '`version`: Show the current installed version of Tabor.\n')
    parser.add_argument('--file', help='The path to the .tabor file.')
    parser.add_argument('--db', help='The name of the PostGIS database to connect to.')
    parser.add_argument('--username', help='The username of a database user.')
    parser.add_argument('--password', help='The password of a database user.', default=None)
    parser.add_argument('--host', help='The hostname of the PostGIS database to connect to.', default="localhost")
    parser.add_argument('--port', help='The port of the PostGIS database to connect to.', default=5432)
    parser.add_argument('--ignore', nargs="+", help='Any tables to ignore when writing to the .tabor file.', default=[])


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

        write(args.file, args.db, args.username, args.password, args.host, args.port, args.ignore)
    elif args.command == "load":
        if not args.file:
            raise Exception("You must provide one file to load from (--file)")

        if not args.db:
            raise Exception("You must provide a PostGIS database to load into (--db)")

        if not args.username:
            raise Exception("You must provide a PostGIS database user to connect to your database (--username)")

        load(args.file, args.db, args.username, args.password, args.host, args.port)
    elif args.command == "version":
        print(VERSION)
    else:
        raise Exception(f"No idea what '{args.command}' is!")

    sys.exit(0)
