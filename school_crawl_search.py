"""V9 grounded retrieval of locally reviewed school snapshots; no network calls."""
import json,re,unicodedata
from pathlib import Path
from functools import lru_cache
ROOT=Path(__file__).resolve().parent
SYNONYMS={'重修':['重補修','補修','被當','學分不足','學分沒過'],'補考':['學期補考','段考補考','成績不及格'],'畢業':['畢業條件','畢業門檻','學分取得'],'請假':['病假','事假','補假'],'行事曆':['學校行事曆','日期','開學'],'獎懲':['警告','小過','大過','嘉獎']}
STOP=('跳到主要內容區','漢堡鈕選單','Copyright©','登入成功','Share','Toggle fullscreen','Zoom in/out')
def normalize(s):return unicodedata.normalize('NFKC',str(s or '')).lower().replace(' ', '')
def expand_query(q):
 q=normalize(q);terms=[q]
 for key,words in SYNONYMS.items():
  if key in q or any(w in q for w in words):terms += [key]+words
 terms += re.findall(r'[\u4e00-\u9fff]{2,}|[a-z0-9]{3,}',q)
 return list(dict.fromkeys(t for t in terms if len(t)>1))[:18]
def split_chunks(text,chunk_size=850,overlap=90):
 lines=[x.strip() for x in str(text or '').splitlines() if x.strip() and not any(x.startswith(s) for s in STOP)]
 text='\n'.join(lines)
 if not text:return []
 out=[];step=chunk_size-overlap
 for pos in range(0,len(text),step):
  out.append((pos,text[pos:pos+chunk_size]))
  if pos+chunk_size>=len(text):break
 return out
@lru_cache(maxsize=1)
def load_records():
 p=ROOT/'school-crawl-data.json'
 if not p.exists():return None
 d=json.loads(p.read_text(encoding='utf-8'))
 return d.get('records',[])
def search_pages(query,limit=5):
 records=load_records()
 if records is None:return {'status':'not_collected','matches':[]}
 terms=expand_query(query);scored=[];seen=set()
 for row in records:
  title=str(row.get('title',''));url=str(row.get('url',''))
  if not url.startswith('https://www.ykvs.ntpc.edu.tw/') and not url.startswith('https://ykvs.ntpc.edu.tw/'):continue
  for pos,chunk in split_chunks(row.get('text','')):
   ntitle=normalize(title);nchunk=normalize(chunk)
   hits=[t for t in terms if t in ntitle or t in nchunk]
   if not hits:continue
   score=sum((15 if t in ntitle else 0)+min(nchunk.count(t),4)*3 for t in hits)
   score+=min(len(hits),5)*3
   if row.get('source_type')=='public_school_pdf':score+=5
   if len(chunk)<70:score-=10
   key=(url,pos)
   if key in seen:continue
   seen.add(key)
   scored.append((score,{'title':title,'url':url,'excerpt':chunk[:850], 'retrieved_at':row.get('retrieved_at'),'source_type':row.get('source_type','public_school_webpage'),'page_count':row.get('page_count'),'chunk_offset':pos,'score':score}))
 scored.sort(key=lambda x:-x[0]);lim=max(1,min(10,int(limit)))
 return {'status':'found' if scored else 'not_found','matches':[v for _,v in scored[:lim]],'query_terms':terms,'total_candidates':len(scored),'note':'來源為擷取快照，非即時資料；日期、費用與個案須以校方最新公告為準。'}
