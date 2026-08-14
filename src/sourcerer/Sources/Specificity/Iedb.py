"""
IEDB - B-cell/antibody receptor sequences and assay annotations

IEDB (https://www.iedb.org/) publishes receptor sequences as a single bulk
ZIP export and assay data through a PostgREST API
(https://query-api.iedb.org/api/v1). A table is not an index into many
separately downloadable files: the table itself *is* the data unit, so each
table produces exactly one DataUnit.

IEDB has no HTML search form to scrape, so harvestSchema returns a hand
curated snapshot rather than one built from a live page.
"""

# Info
__author__ = 'Pramod Shinde'

# Imports
import hashlib
import json
import logging
import zipfile
from datetime import UTC
from pathlib import Path

import pandas

# Sourcerer imports
from sourcerer.Sources.Specificity.Paginate import pageByRange
from sourcerer.Exceptions import IedbParseError
from sourcerer.Http import hashFile
from sourcerer.Sources.Base import DataUnit, DownloadResult, SourceBase

log = logging.getLogger(__name__)

#: Endpoints.
API_BASE = 'https://query-api.iedb.org/api/v1'
BULK_URL = 'https://www.iedb.org/downloader.php?file_name=doc/receptor_full_v3.zip'

#: Rows requested per page from the PostgREST API.
API_PAGE_SIZE = 2000

#: table -> (unit_id, url). bcr and tcr share one bulk ZIP; bcell and
#: bcr_to_bcell are each their own API endpoint.
_TABLE_SOURCE = {
    'bcr': ('bcr_full_v3.csv', BULK_URL),
    'tcr': ('tcr_full_v3.csv', BULK_URL),
    'bcell': ('bcell_search.json', API_BASE + '/bcell_search'),
    'bcr_to_bcell': ('bcr_to_bcell.json', API_BASE + '/bcr_to_bcell'),
}

#: Tables served from the shared receptor bulk ZIP rather than the API.
_BULK_TABLES = frozenset(['bcr', 'tcr'])

#: qualitative_measure has no server-side filter on bcell_search, so it is
#: applied client-side after fetching; this is its known controlled
#: vocabulary.
_QUALITATIVE_MEASURES = ('Positive', 'Positive-High', 'Positive-Intermediate',
                         'Positive-Low', 'Negative')


def _rowHash(row):
    """
    Build a short content hash for an annotation row.

    Arguments:
      row (pandas.Series): a row of upstream columns, before provenance
        columns are added.

    Returns:
      str: the first 12 hex characters of a SHA-256 digest.
    """
    key = '|'.join(str(x) for x in row.tolist())

    return hashlib.sha256(key.encode('utf-8')).hexdigest()[:12]


def _findZipMember(archive, filename):
    """
    Locate a member of the receptor bulk ZIP by its filename.

    Arguments:
      archive (zipfile.ZipFile): the opened archive.
      filename (str): the filename to find, ignoring any directory prefix.

    Returns:
      str: the matching member name.

    Raises:
      IedbParseError: if no member has that filename.
    """
    for member in archive.namelist():
        if Path(member).name == filename:
            return member

    raise IedbParseError(
        "'%s' not found in %s; the receptor bulk export layout has changed"
        % (filename, BULK_URL))


class IedbSource(SourceBase):
    """
    The IEDB specificity source.
    """

    name = 'iedb'
    description = ('IEDB: curated B-cell/antibody receptor sequences and '
                   'assay annotations')
    homepage = 'https://www.iedb.org/'
    collections = ('bcr', 'tcr', 'bcell', 'bcr_to_bcell')
    collection_help = {
        'bcr': 'BCR (antibody) receptor sequences, from the receptor bulk export',
        'tcr': 'TCR receptor sequences, from the same bulk export, kept for reference',
        'bcell': 'B-cell assay records: antigen, epitope and qualitative outcome',
        'bcr_to_bcell': 'join table linking BCR receptor groups to B-cell assay records',
    }

    #: TODO: confirm exact license wording against https://www.iedb.org/about
    #: before this is relied on for redistribution terms.
    license = 'Freely available; see https://www.iedb.org/about'
    citation = (
        'Vita R, Mahajan S, Overton JA, Dhanda SK, Martini S, Cantrell JR, '
        'Wheeler DK, Sette A, Peters B. The Immune Epitope Database (IEDB): '
        '2018 update. Nucleic Acids Res. 2019;47(D1):D339-D343. '
        'doi:10.1093/nar/gky1006',
    )

    def harvestSchema(self):
        """
        Build the hand curated snapshot.

        There is no live form to scrape, so this returns the same field
        definitions packaged in schema.yaml, timestamped now. `sourcerer
        schema refresh --source iedb` exists mainly so the timestamp and any
        future edits to this method stay reproducible the same way a real
        harvest would.

        Returns:
          SourceSchema: the snapshot.
        """
        from datetime import datetime

        from sourcerer.Schema import Collection, Field, SourceSchema
        from sourcerer.Version import __version__

        collections = {
            'bcr': Collection(name='bcr'),
            'tcr': Collection(name='tcr'),
            'bcell': Collection(name='bcell', fields=(
                Field(name='qualitative_measure',
                      values=_QUALITATIVE_MEASURES),
            )),
            'bcr_to_bcell': Collection(name='bcr_to_bcell'),
        }

        return SourceSchema(
            source=self.name,
            harvested=datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ'),
            harvested_by=('sourcerer %s (hand curated, not scraped: IEDB '
                          'exposes no HTML form)' % __version__),
            source_urls={'receptor_bulk': BULK_URL, 'api': API_BASE},
            collections=collections)

    def searchUnits(self, query):
        """
        Resolve a query to the one DataUnit its table represents.

        A table is not an index of many files; the table itself is the unit,
        so there is always exactly one.

        Arguments:
          query (Query): the validated request.

        Returns:
          list: a single DataUnit.
        """
        unit_id, url = _TABLE_SOURCE[query.collection]

        return [DataUnit(unit_id=unit_id, collection=query.collection, url=url,
                         metadata=dict(query.filters))]

    def fetchUnit(self, unit, outdir, resume=True, progress=True):
        """
        Download one table.

        Arguments:
          unit (DataUnit): what to fetch.
          outdir (Path): the mirror root.
          resume (bool): continue an interrupted transfer if possible.
          progress (bool): show a progress bar.

        Returns:
          DownloadResult: the outcome.
        """
        if unit.collection in _BULK_TABLES:
            return self._fetchFromBulkZip(unit, outdir, resume=resume,
                                          progress=progress)

        return self._fetchFromApi(unit, outdir)

    def _fetchFromBulkZip(self, unit, outdir, resume=True, progress=True):
        """
        Fetch the shared receptor bulk ZIP and extract one table from it.

        The ZIP is cached at a fixed path under outdir: a rerun with the file
        already present reuses it (HttpClient.fetch skips a download whose
        destination already exists), so fetching bcr and then tcr in the same
        output directory downloads the ZIP only once.

        Arguments:
          unit (DataUnit): the bcr or tcr table.
          outdir (Path): the mirror root.
          resume (bool): continue an interrupted ZIP transfer if possible.
          progress (bool): show a progress bar for the ZIP transfer.

        Returns:
          DownloadResult: the outcome, describing the extracted table file.
        """
        zip_dest = Path(outdir) / 'receptor_full_v3.zip'
        self.client.fetch(unit.url, zip_dest, resume=resume, progress=progress)

        dest = self.resolveOutputPath(unit, outdir)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_dest) as archive:
            member = _findZipMember(archive, unit.unit_id)
            with archive.open(member) as source, open(dest, 'wb') as target:
                target.write(source.read())

        return DownloadResult(unit=unit, path=dest, sha256=hashFile(dest),
                              size_bytes=dest.stat().st_size)

    def _fetchFromApi(self, unit, outdir):
        """
        Page the PostgREST API for one table and write it as JSON.

        Arguments:
          unit (DataUnit): the bcell or bcr_to_bcell table.
          outdir (Path): the mirror root.

        Returns:
          DownloadResult: the outcome.
        """
        records = []
        for batch in pageByRange(self.client, unit.url, page_size=API_PAGE_SIZE):
            records.extend(batch)

        dest = self.resolveOutputPath(unit, outdir)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(records))

        return DownloadResult(unit=unit, path=dest, sha256=hashFile(dest),
                              size_bytes=dest.stat().st_size)

    def readUnit(self, path, unit, chunksize=50000):
        """
        Open a downloaded table.

        Arguments:
          path (Path): the downloaded file.
          unit (DataUnit): what it is.
          chunksize (int): rows per chunk, for the CSV tables. The JSON
            tables are modest enough to read as a single chunk.

        Returns:
          tuple: ({}, iterator of raw record chunks). IEDB tables carry no
          per-unit metadata line.
        """
        if unit.collection in _BULK_TABLES:
            return {}, pandas.read_csv(path, chunksize=chunksize, dtype=str,
                                       na_filter=False)

        with open(path) as handle:
            records = json.load(handle)

        return {}, iter([pandas.DataFrame.from_records(records)])

    def normalizeChunk(self, metadata, chunk, unit, offset, report):
        """
        Pass a chunk's columns through unchanged, applying provenance and any
        filter the fetch step could not apply server-side.

        Arguments:
          metadata (dict): unused; IEDB tables carry no per-unit metadata.
          chunk (pandas.DataFrame): raw records, IEDB's own columns.
          unit (DataUnit): what they came from.
          offset (int): unused; kept for interface parity with SourceBase.
          report (dict): counters to accumulate into.

        Returns:
          pandas.DataFrame: the chunk with provenance columns added.
        """
        report['rows_in'] += len(chunk)

        frame = self._applyClientFilter(chunk, unit)

        # apply(..., axis=1) on an empty frame cannot infer a row shape, so it
        # is skipped rather than trusted to return an empty result.
        if len(frame):
            row_hash = frame.apply(_rowHash, axis=1)
        else:
            row_hash = pandas.Series([], dtype=str, index=frame.index)

        frame = frame.copy()
        frame['sourcerer_source'] = self.name
        frame['sourcerer_collection'] = unit.collection
        frame['sourcerer_unit_id'] = unit.unit_id
        frame['sourcerer_row_hash'] = row_hash

        report['rows_out'] += len(frame)

        return frame

    def _applyClientFilter(self, frame, unit):
        """
        Apply qualitative_measure filtering that bcell_search cannot do itself.

        Arguments:
          frame (pandas.DataFrame): raw records for one chunk.
          unit (DataUnit): the table, carrying the resolved filters.

        Returns:
          pandas.DataFrame: the filtered chunk, or the chunk unchanged for
          tables and filters this does not apply to.
        """
        wanted = (unit.metadata or {}).get('qualitative_measure')
        if not wanted or wanted == '*' or 'qualitative_measure' not in frame.columns:
            return frame

        return frame[frame['qualitative_measure'] == wanted]
