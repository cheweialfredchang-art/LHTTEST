#!/usr/bin/env python3
"""Compare two crawl snapshots without crawling or deleting the older one."""
import argparse,json,hashlib
from pathlib import Path

def diff(old,new):
 def index(d):return {r['url']:r for r in d.get('records',[]) if r.get('url')}
 a,b=index(old),index(new)
 changed=[u for u in a.keys()&b.keys() if hashlib.sha256(str(a[u].get('text','')).encode()).digest()!=hashlib.sha256(str(b[u].get('text','')).encode()).digest()]
 return {'added':sorted(b.keys()-a.keys()),'removed':sorted(a.keys()-b.keys()),'changed':sorted(changed),'unchanged_count':len(a.keys()&b.keys())-len(changed),'note':'removed 表示本次快照未包含，不代表官方網站已刪除'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('old');p.add_argument('new');p.add_argument('--output',default='crawl-diff-v9.json');x=p.parse_args()
 result=diff(json.loads(Path(x.old).read_text(encoding='utf-8')),json.loads(Path(x.new).read_text(encoding='utf-8')))
 Path(x.output).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print({k:len(v) if isinstance(v,list) else v for k,v in result.items() if k!='note'})
