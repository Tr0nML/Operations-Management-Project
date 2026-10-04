"""Retrieve source cards locally; no generative model, API key or network call.
Example: python code/ask_evidence.py "How should capacity diversion be interpreted?"
The answer is a source-summary retrieval result, not proof the query is fully answered.
"""
from pathlib import Path
import json, sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
ROOT=Path(__file__).resolve().parents[1]
cards=json.loads((ROOT/'data/clean/evidence_cards.json').read_text())
sources={s['id']:s for s in json.loads((ROOT/'data/clean/source_register.json').read_text())}
query=' '.join(sys.argv[1:]).strip()
if not query:
    raise SystemExit('Supply a question after the script name.')
vec=TfidfVectorizer(stop_words='english',ngram_range=(1,2))
X=vec.fit_transform([c['title']+' '+c['summary'] for c in cards])
scores=cosine_similarity(vec.transform([query]),X)[0]
hits=sorted(range(len(cards)),key=lambda i:scores[i],reverse=True)
if scores[hits[0]]<.12:
    print('No reliable match in the curated source cards. Consult the original sources.')
else:
    for i in hits[:2]:
        if scores[i]<.12:continue
        c=cards[i]
        print(c['title']+'\n'+c['summary']+'\n'+c['locator']+'\n'+sources[c['source_id']]['url']+'\n')
