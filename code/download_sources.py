"""Optional re-download of the three core official PDFs using public URLs.

Usage: python code/download_sources.py
Downloads are not required to rerun the project: extracted text is included.
No credentials or access-control bypass are used. Some sites intermittently fail.
Use pdftotext -layout FILE.pdf FILE.txt (Poppler) to recreate extraction text.
"""
from pathlib import Path
import urllib.request, hashlib, json
ROOT=Path(__file__).resolve().parents[1]
sources={s['id']:s for s in json.loads((ROOT/'data/clean/source_register.json').read_text())}
dest=ROOT/'source_documents/full_downloads';dest.mkdir(exist_ok=True)
files={'S1':'dfccil_ar_2024_25.pdf','S2':'dfccil_ar_2023_24.pdf','S3':'world_bank_edfc_icr.pdf'}
for sid,name in files.items():
    target=dest/name
    try:
        req=urllib.request.Request(sources[sid]['url'],headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req,timeout=45) as response:
            data=response.read()
        if not data.startswith(b'%PDF'):raise ValueError('Response was not a PDF')
        target.write_bytes(data)
        print(name,len(data),'bytes',hashlib.sha256(data).hexdigest())
    except Exception as e:
        print(name,'download failed:',str(e),'; use the bundled extracted text and evidence excerpts.')
