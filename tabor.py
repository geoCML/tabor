from argparse import ArgumentParser

from src.tabor_file import TaborFile

import sys

sys.tracebacklimit = -1


def read(file_path: str) -> None:
    """
    Converts a .tabor file to a PostGIS schema query

    :param file_path:   the path to the .tabor file you want to read
    """
    try:
        tabor_src = TaborFile(file_path)
    except Exception as e:
        print(e)
        return False

    print(tabor_src.to_psql())


def write(schema_query: str, file_path: str) -> None:
    """
    Converts a PostGIS schema query into a .tabor file

    :param schema_query:    the query to be converted into a .tabor file
    :param file_path:       the path to the new .tabor file
    """
    tabor_src = TaborFile(file_path, psql=schema_query)
    tabor_src.write()
    print(f"Wrote .tabor file to {file_path}")


if __name__ == "__main__":
    parser = ArgumentParser(description='tabor <command> <flags>')
    parser.add_argument('command', help='`read`: Converts a .tabor file into a PostGIS schema query.\n' +
                                        '`write`: Converts a PostGIS schema query into a .tabor file. (WIP Feature)\n')
    parser.add_argument('--file', help='The path to the .tabor file.')
    parser.add_argument('--queries', help='The list of queries to convert into a .tabor file', nargs='+')

    args = parser.parse_args()

    if args.command == "read":
        if not args.file:
            raise Exception("You must provide one file to read from (--file)")
        read(args.file)
    elif args.command == "write":
        if not args.file:
            raise Exception("You must provide one file to write to (--file)")

        if not args.queries:
            raise Exception("You must provide at least one PostGIS Query to write to the .tabor file (--queries)")
        write(args.queries, args.file)
    else:
        raise Exception(f"No idea what '{args.command}' is!")

    sys.exit(0)
