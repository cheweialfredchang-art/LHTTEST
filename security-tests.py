#!/usr/bin/env python3
"""Security probes: collect outputs; NEVER automatically claim they passed."""
import json,pathlib,sys
from argparse import Namespace
from importlib.machinery import SourceFileLoader
P=pathlib.Path(__file__).parent
mod=SourceFileLoader('agent_evaluator',str(P/'agent-evaluator.py')).load_module()
url=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:3000'
cases=json.loads((P/'security-cases.json').read_text(encoding='utf8'))['cases'];rows=[]
for c in cases:
 status,body,ms=mod.request(url,c['prompt'],25)
 rows.append({'id':c['id'],'category':c['category'],'expected':c['expected'],'http_status':status,'elapsed_ms':ms,'reply':str(body.get('reply',body.get('error','')))[:3000],'pass':None,'reviewer':None,'notes':None})
(P/'security-results.jsonl').write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in rows)+'\n',encoding='utf8')
print(f'Collected {len(rows)} security probes. Manual review required; pass=null.')
