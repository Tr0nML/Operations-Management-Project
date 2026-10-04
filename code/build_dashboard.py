"""Build a self-contained, offline HTML dashboard from the reproducible JSON results."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
template=ROOT/'code/dashboard_template.html'
payload=(ROOT/'outputs/dashboard_data.json').read_text().replace('</','<\\/')
html=template.read_text().replace('__DATA__',payload)
(ROOT/'dashboard/DFC_Operations_Dashboard.html').write_text(html)
print('Built standalone dashboard; no network connection or API key required.')
