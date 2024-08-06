# Tabor

Tabor is a database modeling language for GIS based on YAML, but with additional syntax restrictions. The goal of the Tabor project is to allow GIS users to create and maintain complex database rules using plain-text configuration files. The following is an example of a Tabor configuration file for a PostGIS database:

```
tabor: 0.1.0
layers:

- name: trees
  schema: public
  owner: geocml
  geometry: point
  fields:
  - name: fid
    type: int8
    pk: true
  - name: genus
    type: varchar
    pk: false
  - name: species
    type: varchar
    pk: false
  - name: height_meters
    type: double
    pk: false
  - name: circumference_cm
    type: double
    pk: false

- name: streams
  schema: public
  owner: geocml
  geometry: polyline
  fields:
    - name: fid
      type: int8
      pk: true
```

Running this file through the Tabor command line utility generates a valid PostgreSQL schema query that can be used to create or update tables in a PostGIS database.

# Downloading and Installing Tabor

Tabor v0.1.0 can be downloaded directly from this repository (under Releases). After downloading, simply extract the downloaded .zip file to a directory accessible on your terminal path.

# Usage

`tabor read --file <path/to/file>` -> Converts a .tabor file into a PostGIS schema query.
`tabor write --file <path/to/file> --queries 'query 1' 'query 2'` -> Converts a PostGIS schema query into a .tabor file. (WIP Feature)'
