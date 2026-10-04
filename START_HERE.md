# DFC Operations Management WAI project

This package supports an individual IIM Ranchi Working with AI assignment on Indian Railways and DFCCIL. It contains a 12-page report, a ten-slide presentation, an offline dashboard with seven visuals, actual prompt records, a recording/viva guide, audited data and reproducible analysis.

## Read first

1. Read `submission/WAI_DFC_Report.pdf` for the fixed-layout report. Use the DOCX to add your name and roll number.
2. Open `dashboard/DFC_Operations_Dashboard.html` directly in a desktop browser. Internet, installation and API keys are unnecessary. Change the year, corridor, forecast model, diversion and cost assumptions.
3. Review `submission/WAI_DFC_Presentation_Final.pptx` and the recording/viva guide. Charts and the scenario table are editable.
4. Complete `SUBMISSION_CHECKLIST.md`. The student recording and actual GitHub/Drive link remain to be supplied.

## What the evidence establishes

- DFC train movements rose from 88,225 to 130,116 between FY2023–24 and FY2024–25: **47.5%**.
- EDFC unweighted mean monthly speed fell from **45.11 to 41.65 km/h**. Mean reported wagon turnround rose from **1.22 to 1.64 days**.
- Day-adjusted naive forecasting achieved **4.66% test WAPE**, against **9.94% for random forest**, across twelve rolling one-month predictions.
- Historical diversion scenarios illustrate uneven relief. They do not measure current capacity release or a nationwide causal effect.
- Pilot economics are hypothetical. The base case is **INR 0.50 crore first-year net benefit**, with all inputs disclosed.

## Folder map

| Folder | Contents |
|---|---|
| `submission/` | Report DOCX/PDF, slides, prompt logbook, recording/viva guide |
| `dashboard/` | Self-contained interactive HTML |
| `data/raw/` | Reported cells, capacity transcription and feasibility count audit |
| `data/clean/` | Clean monthly panel, total counts, dictionary, discrepancy log, source register and evidence cards |
| `outputs/` | Annual summaries, forecast predictions/errors, correlations, scenarios and audit receipts |
| `code/` | Commented extraction, analysis, figures, dashboard, chatbot and document scripts |
| `figures/` | Seven publication-ready figures |
| `source_documents/` | Extracted source text, selected original PDF pages and source manifest |
| `screenshots/` | Actual browser captures and source-table images |

## Reproduce the analysis

Use Python 3.11 or later. From the project directory:

```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell, instead:
# .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python code/run_all.py
```

The workflow requires no network after dependencies are installed. It reads the bundled official-report text. Outputs are regenerated under the same filenames. Versions used in the authoring environment are recorded in `outputs/runtime_versions.json`.

To inspect the evidence chatbot from the command line:

```bash
python code/ask_evidence.py "How should freight diversion and capacity be interpreted?"
```

The browser chatbot and command-line chatbot both retrieve curated summaries. The Python version uses words/bigrams; the browser version uses token TF-IDF. Neither is an unrestricted generative chatbot.

## Data and methods

Fiscal years run April–March. Total train counts cover December 2020–March 2025; core corridor data covers April 2021–March 2025. The selected corridor trains/day table starts April 2022. Two February 2023 corridor train-rate cells and one March 2023 WDFC speed cell are excluded from clean use; raw values remain intact. No missing observation is imputed.

Annual network trains/day uses exact counts divided by calendar days. Corridor annual speed and turnround use unweighted monthly means. GTKM is gross tonne-kilometres, not net cargo tonnage. Tiny source rounding differences are retained rather than forced to reconcile.

Models are selected using April 2023–March 2024 validation MAE. April 2024–March 2025 is the test year. At each origin, all features and fitting observations precede the target month. This is rolling one-step forecasting, not a single twelve-month forecast. Historical publication vintages were not reconstructed, so this is retrospective evaluation rather than a proven real-time deployment. The optional April 2025 prediction is historical, not a current 2026 forecast.

Capacity scenarios use World Bank FY2022–23 conventional traffic, already partly post-DFC. They hold passenger/other trains fixed and apply equal train weights. A normalized effective-capacity denominator is inferred from published utilization because nominal capacity uses a different convention. These results must not be interpreted as engineering path availability.

## Recreating documents and slides

Analytical reproduction uses only ordinary Python packages. The report/log/guide builder additionally uses `python-docx`; it is in `code/build_documents.py`. Rendering used the authoring environment's document renderer. Word may paginate slightly differently if fonts or print settings change; the PDF preserves the verified 12-page layout.

`code/build_slides.mjs` documents the slide authoring process using the first-party `@oai/artifact-tool` and its validation helpers. That authoring runtime is environment-specific, so the exported PPTX is supplied for ordinary PowerPoint editing. It is not needed to reproduce any analytical result. Do not expect the slide builder to work with Python dependencies alone.

## Attribution and limitations

Ten sources are listed in `data/clean/source_register.json` and in the report's APA references. Three core PDFs were downloaded; selected original pages and full extracted text are retained. `code/download_sources.py` can re-fetch the full PDFs, subject to website availability. Source documents retain their original ownership; the package does not confer a reuse licence.

ChatGPT assisted research, coding, interpretation and drafting. The logbook preserves actual available user instructions and labels proposed follow-up prompts. The student should review, personalize and be able to explain every claim. No interviews, deployment, personal operational data or realized savings are represented as completed work.
