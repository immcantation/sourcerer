"""
Download provenance for annotation sources

A separate writer from sourcerer.Provenance.writeDownloadMetadata: an
annotation download represents a database's current state rather than one
more addition to a growing repertoire dataset, so each run replaces the
record instead of merging into it. Kept apart from Provenance.py itself so
this does not change what repertoire sources rely on.
"""

# Info
__author__ = 'Pramod Shinde'

# Imports
from pathlib import Path

import yaml

# Sourcerer imports
from sourcerer.Provenance import (DOWNLOAD_METADATA, METADATA_VERSION,
                                  commandLine, timestamp)
from sourcerer.Version import __version__


def writeAnnotationMetadata(out, source, table, filters, limit, units,
                            schema=None, license=None, citation=None):
    """
    Write the provenance record for an annotation download directory.

    Unlike Provenance.writeDownloadMetadata, this always replaces the file
    rather than merging into whatever was already there.

    Arguments:
      out (Path): the download root. The file is written at its top level.
      source (str): the annotation database name.
      table (str): the table (or 'all') downloaded.
      filters (dict): the filters the user supplied.
      limit (int): the table cap, or None.
      units (list): unit records from Provenance.buildUnitRecord.
      schema (SourceSchema): the snapshot the query resolved against, if known.
      license (str): the source's data license, if known. Recorded so a reader
        of this directory alone, with no access to sourcerer's own docs, still
        knows the terms the data was obtained under.
      citation (tuple): the source's requested citation(s), if known, for the
        same reason.

    Returns:
      Path: the file written.
    """
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    path = out / DOWNLOAD_METADATA

    run = {
        'finished': timestamp(),
        'command': commandLine(),
        'collection': table,
        'filters': dict(filters or {}),
        'limit': limit,
        'formats': ['tsv'],
        'units': len(units),
    }
    if schema is not None:
        run['schema_harvested'] = schema.harvested
        run['schema_harvested_by'] = schema.harvested_by

    record = {
        'sourcerer_metadata_version': METADATA_VERSION,
        'source': source,
        'generated_by': 'sourcerer %s' % __version__,
    }
    if license is not None:
        record['data_license'] = license
    if citation:
        record['data_citation'] = list(citation)
    record['runs'] = [run]
    record['units'] = list(units)

    with open(path, 'w') as handle:
        yaml.safe_dump(record, handle, sort_keys=False, default_flow_style=False)

    return path
