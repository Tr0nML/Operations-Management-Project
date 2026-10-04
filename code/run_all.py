"""One-command reproduction of data, results, figures and offline dashboard.

Use: python code/run_all.py
The included source text makes this workflow independent of live websites.
Document and slide authoring are optional and separate from analytical reproduction.
"""
from pathlib import Path
import subprocess, sys
HERE=Path(__file__).resolve().parent
for name in ['extract_data.py','run_analysis.py','make_figures.py','build_dashboard.py']:
    print('\nRunning '+name,flush=True)
    subprocess.run([sys.executable,str(HERE/name)],check=True)
print('\nComplete. See outputs/, figures/ and dashboard/.')
