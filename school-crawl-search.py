"""Search manually harvested public pages; evidence only, no unsupported inference."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def search_pages(query,limit=5):
 q=str(query or '').strip()
 path=ROOT/'school-crawl-data.json'
 if not path.exists():return {'status':'not_collected','matches':[],'note':'請先在本機執行 school-crawler.py 並審核 JSON 後部署。'}
 try:data=json.loads(path.read_text(encoding='utf-8'))
 except (ValueError,OSError):return {'status':'invalid_data','matches':[]}
 terms=[x for x in re.findall(r'[\u4e00-\u9fff]{2,}|[a-zA-Z0-9]{2,}',q.lower())]
 if not terms:terms=[q.lower()]
 scored=[]
 for row in data.get('records',[]):
  title=str(row.get('title',''));body=str(row.get('text',''))
  score=sum(8*title.lower().count(t)+body.lower().count(t) for t in terms)
  if score:
   first=min((body.lower().find(t) for t in terms if t in body.lower()),default=0)
   snippet=body[max(0,first-100):first+650]
   scored.append((score,{'title':title,'url':row.get('url'),'excerpt':snippet,'retrieved_at':row.get('retrieved_at'),'source_type':row.get('source_type','public_school_webpage'),'score':score}))
 scored.sort(key=lambda x:-x[0])
 return {'status':'found' if scored else 'not_found','matches':[r for _,r in scored[:max(1,min(8,limit))]],'note':'網頁擷取快照，非即時資訊；對於重修、補修、期限等須核對最新正式規章與公告。'}
