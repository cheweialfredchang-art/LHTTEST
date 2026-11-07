#!/usr/bin/env python3
"""Offline retrieval benchmark. Does not claim factual answer correctness."""
import json,sys
from pathlib import Path
from school_crawl_search import search_pages
cases=json.loads(Path('evaluation-100-v9.json').read_text(encoding='utf-8'))['cases']
rows=[]
for c in cases:
 result=search_pages(c['question'],5)
 rows.append({'id':c['id'],'topic':c['topic'],'has_source':bool(result['matches']),'top_url':result['matches'][0]['url'] if result['matches'] else None,'verified_correct':None})
out={'count':len(rows),'source_coverage':sum(r['has_source'] for r in rows)/len(rows),'accuracy':None,'note':'source coverage only; accuracy requires manually reviewed official answers','results':rows}
Path('evaluation-report-v9.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print('Questions:',out['count'],'Source coverage:',f"{out['source_coverage']:.1%}",'Verified accuracy: NOT MEASURED')
