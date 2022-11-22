# Approach to GIS data modeling

## Purpose

To provide a means of creating/updating/maintaining database schemas for quality GIS data.

## Desired outcomes

- A lightweight, filesystem-based, human and machine-readable syntax for generating PostGIS schemas

## Assumptions

- How database schemas are used by GIS users & database administrators
- GIS users know how to use a GIS application
- Understanding of a programming language is not a prerequisite

## Technical approach

1) a plaintext syntax for describing a GIS schema should map to PostGreSQL
   - plaintext files should contain fields for GIS features
   - plaintext files should contain data constraints
   - plaintext files should define relationship between features (spatial relationship & inheritance)
2) Output of PostGreSQL files (conforming to GIS schema) can be used in a GIS database
3) Data is loaded into database

## References

- https://desktop.arcgis.com/en/arcmap/10.3/manage-data/geodatabases/a-note-about-the-use-of-uml-for-geodatabase-design.htm
