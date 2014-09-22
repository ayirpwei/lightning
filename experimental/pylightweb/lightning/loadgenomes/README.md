Lightning/loadgenomes
=======================
## templates/
defines a set of visualizations for a website

## addPerson.py
Adds a person to the Tile Library

* Inputs: a human FASTJ file, csv snapshot of current library-tilevariants
  * csv snapshot can be generated by running the following

        ```sql
        => \copy loadgenomes_tilevariant(tile_variant_name, tile_id, population_size, md5sum) to 'curr-data.csv' with csv 
        ```
* Outputs: tilevariant.csv, varannotation.csv, update.sql, Library.csv
  * (Outputs can be loaded into postgres by running)

        ```sql
        => \copy loadgenomes_tilevariant from 'tilevariant.csv' with csv 
        => \copy loadgenomes_varannotation(tile_variant_id, annotation_type, source, annotation_text, phenotype, created, last_modified) from 'varannotation.csv' with csv
        $ psql lightningdatabase < update.sql
        ```

## addRefAndPopulation.py
begins the Tile Library and can add people to it
* Inputs: a FASTJ file starting with the reference sequence
* Outputs: tile.csv, tilevariant.csv, varannotation.csv, tilelocusannotation.csv, Library.csv
  * Outputs can be loaded into the postgres database by running the following

        ```sql
        => \copy loadgenomes_tile from tile.csv with csv 
        => \copy loadgenomes_tilevariant from 'tilevariant.csv' with csv 
        => \copy loadgenomes_tilelocusannotation(tile_id, assembly, chromosome, begin_int, end_int, chromosome_name) from 'tilelocusannotation.csv' with csv 
        => \copy loadgenomes_varannotation(tile_variant_id, annotation_type, source, annotation_text, phenotype, created, last_modified) from 'varannotation.csv' with csv
        ```

## admin.py
defines the visualization (for an admin) of the models defined in models.py.

## init.py
required for django. Empty

## models.py
defines the models: Tile -> TileVariant -> VarAnnotation
                  -> TileLocusAnnotation
 * A Tile defines the position (path, version, step) of a tile
 * A TileVariant defines a possible tile at the position of its parent Tile
 * A VarAnnotation describes a quality of the TileVariant (a SNP, INDEL, db_xref associated with that sequence)
 * A TileLocusAnnotation is the translation mechanism between Tile positions and other assemblies

## tests.py
tests for website

## urls.py
urls defined for website

## views.py
serves the pages defined for website
