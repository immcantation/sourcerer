Release Notes
================================================================================

Version 0.1.0: 2026.08.04
-------------------------------------------------------------------------------

Initial release.

General:

+ Added the ``sourcerer`` commandline tool, with one module per external
  immune-repertoire database and OAS_ (Observed Antibody Space) as the first
  source.
+ Added ``sourcerer oas search`` and ``sourcerer oas download``, for both the
  ``paired`` and ``unpaired`` OAS collections, with commandline filter flags
  generated from a checked-in snapshot of the OAS search form rather than
  hardcoded.
+ Added conversion of downloaded data to an AIRR rearrangement TSV, with a
  streaming validation report, and to FASTA.
+ Added ``nf-core/airrflow`` samplesheet generation, one samplesheet per
  converted format, that merges across repeated download runs into the same
  output directory instead of overwriting.
+ Added ``sourcerer schema show`` and ``sourcerer schema refresh``, to inspect
  and re-harvest the stored snapshot of a source's search fields and data unit
  catalog.
+ Added a download provenance record (what was fetched, from where, when, and
  its hash) written alongside every download.

.. _OAS: https://opig.stats.ox.ac.uk/webapps/oas/
