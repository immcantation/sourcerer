sourcerer
================================================================================

``sourcerer`` downloads data from online immune repertoire databases and formats
it for use with the Immcantation_ framework. Each external source is a module;
the first is OAS_ (Observed Antibody Space).

.. _Immcantation: https://immcantation.readthedocs.io
.. _OAS: https://opig.stats.ox.ac.uk/webapps/oas/

Why
--------------------------------------------------------------------------------

Remote databases change. They add organisms, diseases and studies, they rename
search fields, and occasionally they change the format of the files themselves.
Code that hardcodes those details breaks quietly, producing empty result sets or
mislabelled columns rather than errors.

``sourcerer`` keeps a checked-in snapshot of each remote source's search schema
*and* of its downloaded file format. The command line is generated from that
snapshot, so no field list is hardcoded, and a scheduled job re-harvests the
remote schema and opens a pull request whenever it drifts. Breakage shows up as
a reviewable diff and a failing test, not as a silently wrong download.

Usage
--------------------------------------------------------------------------------

.. code-block:: bash

    sourcerer --version
    sourcerer oas download paired --species human --limit 1 --outdir tmp    # To convert to fasta, rerun (hashes any file already on disk)
    sourcerer oas download paired --species human --limit 3 --outdir tmp --format fasta
    cd tmp
    nextflow run nf-core/airrflow -r 5.1.0 \
        -profile docker \
        --mode assembled \
        --input samplesheet_airrflow_fasta.tsv \
        --outdir airrflow_out -c ../airrflow.config \
        --clonal_threshold 0.2 -resume


License
--------------------------------------------------------------------------------

This work is licensed under the `GNU Affero General Public License 3 (AGPL-3)
<https://www.gnu.org/licenses/agpl-3.0.en.html>`_.
