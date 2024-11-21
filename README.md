# Tabor

Tabor is a database modeling language for GIS based on YAML, but with additional syntax restrictions. The goal of the Tabor project is to allow GIS users to create and maintain complex database rules using plain-text configuration files. The following is an example of a Tabor configuration file for a PostGIS database:

```
tabor: 0.3.0
layers:

- name: grass
  schema: public
  owner: geocml
  geometry: polygon
  srid: 4326
  fields:
    - name: fid
      type: int
      pk: true

- name: trees
  schema: public
  owner: geocml
  geometry: point
  srid: 4326
  fields:
  - name: fid
    type: int
    pk: true
  - name: genus
    type: text
  - name: species
    type: text
  - name: height_meters
    type: numeric
  - name: circumference_cm
    type: numeric
  constraints:
    - name: on
      layer: grass

- name: streams
  schema: public
  owner: geocml
  geometry: polyline
  srid: 4326
  fields:
    - name: fid
      type: int
      pk: true
```

Running this file through the Tabor command line utility generates a valid PostgreSQL schema query that can be used to create or update tables in a PostGIS database.

# Downloading and Installing Tabor

Tabor can be downloaded directly from this repository (under Releases). After downloading, simply extract the downloaded .zip file to a directory accessible on your terminal path.

# Usage

`tabor read --file <path/to/file>` -> Converts a .tabor file into a PostGIS schema query.

`tabor write --file <path/to/file> --db <name_of_psql_db> --username <name of db user> --password <password of db user?> --host <host of psql db?> --port <port of psql db?> --ignore <tables to ignore?>` -> Converts a PostGIS database to a .tabor file

`tabor load --file <path/to/file> --db <name_of_psql_db> --username <name of db user> --password <password of db user?> --host <host of psql db?> --port <port of psql db?>` -> Loads a PostGIS database from a .tabor file.
