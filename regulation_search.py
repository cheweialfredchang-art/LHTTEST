"""School-specific evidence retrieval. No inference of unprovided procedures or deadlines."""
import json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ALIASES={
 '重修補修':['重修','補修','重補修','重補修課程','重讀','學分沒過','學分不足','被當','不及格','學分不夠','補學分','學分未取得','學期成績不及格'],
 '學期補考':['補考','學期補考','學期成績','學期不及格','成績不及格','學分'],
 '段考補考':['段考','缺考','補行考試','定期評量','定期考試'],
 '學習歷程':['學習歷程','學習成果','多元表現'],
 '學分抵免':['抵免','轉學','轉科','復學'],
}
DETAIL=re.compile('期限|截止|報名|費用|收費|開課|時程|日期|表單|申請表|幾月|何時|哪天|資格|條件|幾分|分數')
def normalize(x):return re.sub(r'\s+','',str(x or '')).lower()
def search_regulations(query,limit=4):
 q=normalize(query)
 if not q:return {'query':query,'matches':[],'status':'empty_query'}
 try:records=json.loads((ROOT/'additional_regulations.json').read_text(encoding='utf-8')).get('records',[])
 except (OSError,ValueError):records=[]
 concepts={group for group,aliases in ALIASES.items() if any(normalize(a) in q for a in aliases)}
 ranked=[]
 for row in records:
  title=normalize(row.get('title'))
  kws=[normalize(x) for x in row.get('keywords',[])]
  category=normalize(row.get('category'))
  score=0
  score+=sum(4 for k in kws if len(k)>1 and k in q)
  score+=sum(3 for a in [title,category] if a and a in q)
  if '重修補修' in concepts and ('重修' in kws or '補修' in kws):score+=25
  if '段考補考' in concepts and ('段考' in kws or '缺考' in kws):score+=12
  if '學期補考' in concepts and '成績考核' in category:score+=8
  if '學習歷程' in concepts and '學習歷程' in category:score+=15
  if '學分抵免' in concepts and '抵免' in title:score+=15
  if score:ranked.append((score,row))
 ranked.sort(key=lambda x:(-x[0],x[1].get('data_id','')))
 matches=[]
 for score,r in ranked[:max(1,min(8,int(limit)))]:
  matches.append({k:r.get(k) for k in ('data_id','title','section_heading','department','unit','content','source_url','publication_date','last_verified_date','review_status')})
 return {'query':query,'concepts':sorted(concepts),'matches':matches,'status':'found' if matches else 'not_found','detail_requested':bool(DETAIL.search(q)),'note':'資料為專案既有摘要及文件索引，非即時查證；未記載的報名期限、費用、開班與資格不得推定。'}
def credit_answer(q,result):
 matches=result['matches']
 if not matches:return None
 primary=next((x for x in matches if '學習評量補充規定' in x.get('title','')),matches[0])
 text=(
  '📚 重修／補修與學分查詢\n\n'
  '依目前收錄的《'+primary.get('title','校方相關規定')+'》摘要：\n'
  '• 學期成績不及格的科目，依規定的基準辦理學期補考，每學期每科目補考一次。\n'
  '• 未取得學分的科目，得依相關規定申請重修或補修。\n\n'
  '⚠️ 目前資料沒有提供可直接確認的本學期重修／補修開課名單、報名期限、費用或完整申請程序；請向教務處註冊組確認，不能把一般規定當成已公告的開班資訊。\n\n'
  '🔗 校方文件來源（專案既有索引，請核對最新版本）\n'
  + str(primary.get('source_url','')) + '\n'
  '文件：'+str(primary.get('title',''))+'\n'
  '資料標示最後核對：'+str(primary.get('last_verified_date','未提供'))
 )
 return text
