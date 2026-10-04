# Source documents

The package retains complete text extracted from three official PDFs and the original pages needed to audit the numerical tables. Full PDFs can be downloaded using `python code/download_sources.py`; the analysis does not require that download.

| Source | Selected physical pages | Printed page numbers | Use |
|---|---|---|---|
| S1 DFCCIL annual report 2024–25 | 49–51 | 47–49 | Train rates, total counts, GTKM, speed and wagon turnround |
| S2 DFCCIL annual report 2023–24 | 74 | 72 | Earlier reported WDFC March 2023 speed for discrepancy check |
| S3 World Bank EDFC completion report | 90 | 85 | Historical conventional-line traffic and utilization |

`source_manifest.json` records original PDF hashes, sizes and selected pages. URLs and bibliographic details for all ten sources are in `data/clean/source_register.json`. Original documents remain the property of their respective publishers. This is a source audit for an academic analysis, not a licence to redistribute their work for other purposes.

To recreate a full extracted text file after downloading its PDF, install Poppler and use `pdftotext -layout input.pdf output.txt`. The included text was generated with that layout-preserving mode. The capacity table is explicitly transcribed in `code/extract_data.py` and can be checked against the S3 excerpt.
