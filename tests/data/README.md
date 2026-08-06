# Test fixtures

Captured from the live Observed Antibody Space (OAS) service on **2026-08-04**.

OAS data is distributed under **CC-BY 4.0**. These files are redistributed here
under that licence for testing purposes and must keep this attribution:

> Olsen TH, Boyles F, Deane CM. *Observed Antibody Space: A diverse database of
> cleaned, annotated, and translated unpaired and paired antibody sequences.*
> Protein Science (2022). <https://doi.org/10.1002/pro.4205>
> <https://opig.stats.ox.ac.uk/webapps/oas/>

Every data fixture is trimmed to the smallest excerpt that exercises the code.
Do not add whole data units: they are hundreds of megabytes and nothing in the
test suite needs more than a few rows.

## Pages

| File | Source | Captured with |
|---|---|---|
| `oas_paired_form.html` | `/webapps/oas/oas_paired/` | `curl` |
| `oas_unpaired_form.html` | `/webapps/oas/oas_unpaired/` | `curl` |
| `oas_paired_search_all.html.gz` | POST to `/webapps/oas/oas_paired/` with every field `*` | `curl -F 'Species=*' ...`, gzipped |
| `oas_dataunit_paired_detail.html` | `/webapps/oas/dataunit_paired?unit=Alsoiussi_2020/csv/SRR11528761_paired.csv.gz` | `curl` |

## Data units

Each keeps the upstream structure exactly: a **two member gzip stream**, where
member one is the JSON metadata line and member two is the CSV. That is not a
detail to normalize away — a naive single member decoder reads only the metadata
and silently reports an empty file.

| File | Upstream path | Layout | Columns | Rows kept |
|---|---|---|---|---|
| `SRR11528761_paired.head.csv.gz` | `paired/Alsoiussi_2020/csv/SRR11528761_paired.csv.gz` | `csv/` | 180 | 19 |
| `1_S1__1_Paired_All.head.csv.gz` | `paired/Phad_2022/csv_paired/1_S1__1_Paired_All.csv.gz` | `csv_paired/` | 198 | 19 |
| `SRR5060321_Heavy_Bulk.head.csv.gz` | `unpaired/Banerjee_2017/csv/SRR5060321_Heavy_Bulk.csv.gz` | `csv/` | 97 | 29 |

The two paired fixtures are both required. They are **not** the same schema:
`csv_paired/` carries nine stems that `csv/` does not (`Isotype`, `Redundancy`,
`c_region`, `complete_vdj`, `fwr4`, `fwr4_aa`, `fwr4_start`, `fwr4_end`,
`v_frameshift`), and it is the majority layout at 452 of 610 paired units. Testing
only the 180 column file would leave the common case uncovered. The
`csv_paired/` fixture also has no run accession in its filename, which is what
pins the rule that unit identifiers are opaque.
