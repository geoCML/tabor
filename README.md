# Tabor

Tabor is a database modeling language for GIS. The goal of the Tabor project is to allow GIS users to create and maintain complex database rules using plain-text YAML configuration files. The following is an example of a YAML configuration file for a PostGIS database:

```
tabor: 0.0.1

Boundary:
  as: b # 'as' is optional and acts as an alias for a class name
  schema: public
  geometry: polygon
  fields:
    boundary_id:
      alias: Boundary ID
      type: text 4

County:
  as: c
  schema: public
  extends: b
  fields:
    county_name:
      alias: County Name
      type: text 25

Population Density:
  as: pop_d
  schema: public
  geometry: point
  fields:
    pop_count:
      type: double
      alias: Population Count
  constraint:
    inside: b

Road:
  as: r
  geometry: polyline
  fields:
    name: 
      type: text 45
      alias: Street Name

Sidewalk:
  as: sw
  geometry: polyline
  constraint:
    buffer:
      around: r
      within: 2 feet
```

Running this YAML file through the Tabor command line utility generates a valid Postgres SQL file that can be used to create or update tables in a PostGIS database.
