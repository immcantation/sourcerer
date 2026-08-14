# Specificity databases (work in progress)

Specificity databases are reference tables  (epitopes, assays, receptor
sequences) rather than repertoire sequencing runs, so they are grouped under
their own `sourcerer specificity` subcommand instead of being one more
top-level source. Each registered database exposes `search` and `download`,
each taking a table as a further subcommand, plus a synthetic `all` table
that acts on every table the database offers.

## IEDB

[IEDB](https://www.iedb.org/) is the first registered database
(`src/sourcerer/Sources/Specificity/Iedb.py`). It offers four tables:

| table            | contents                                                       | source                           |
| ---------------- | -------------------------------------------------------------- | -------------------------------- |
| `bcr`          | BCR (antibody) receptor sequences                              | shared bulk ZIP export           |
| `tcr`          | TCR receptor sequences, kept for reference                     | shared bulk ZIP export           |
| `bcell`        | B-cell assay records: antigen, epitope, qualitative outcome    | PostgREST API (`bcell_search`) |
| `bcr_to_bcell` | join table linking BCR receptor groups to B-cell assay records | PostgREST API (`bcr_to_bcell`) |

### Downloading IEDB data

```bash
# list every registered specificity database
sourcerer specificity list

# download one table
sourcerer specificity iedb download bcr --outdir tmp

# narrow a table down with its filter flags (see --help for what a table supports)
sourcerer specificity iedb download bcell --qualitative-measure Positive --outdir tmp

# download every iedb table
sourcerer specificity iedb download all --outdir tmp

# download every table of every registered specificity database
sourcerer specificity all download --outdir tmp

# see what would be fetched without downloading anything
sourcerer specificity iedb download bcr --outdir tmp --dry-run

# list what a table contains without downloading it
sourcerer specificity iedb search bcell --qualitative-measure Positive -o hits.tsv
```

Referece command: `sourcerer specificity iedb download bcell --help`.
