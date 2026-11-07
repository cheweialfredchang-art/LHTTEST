#!/usr/bin/env python3
"""Bounded, robots-aware school crawler with opt-in host-scoped TLS diagnostic mode."""
import argparse, collections, datetime, html, io, json, random, re, ssl, time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit, urldefrag
from urllib.request import Request, build_opener, HTTPSHandler, HTTPRedirectHandler
from urllib.error import HTTPError, URLError
from urllib.robotparser import RobotFileParser

ROOT=Path(__file__).resolve().parent
DOC_EXT=('.pdf','.doc','.docx','.xls','.xlsx','.ppt','.pptx')
SKIP_EXT=('.jpg','.jpeg','.png','.gif','.webp','.svg','.ico','.mp4','.mp3','.zip','.rar','.css','.js','.woff','.woff2')
NOW=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()

class Page(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True);self.links=[];self.title=[];self.text=[];self.hidden=0;self.in_title=False
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='a' and a.get('href'):self.links.append(a['href'])
  if tag in ('script','style','noscript','svg','nav','footer'):self.hidden+=1
  if tag=='title':self.in_title=True
  if tag in ('p','div','li','h1','h2','h3','tr','br','section','article'):self.text.append('\n')
 def handle_endtag(self,tag):
  if tag in ('script','style','noscript','svg','nav','footer'):self.hidden=max(0,self.hidden-1)
  if tag=='title':self.in_title=False
 def handle_data(self,data):
  if self.in_title:self.title.append(data)
  if not self.hidden and not self.in_title:self.text.append(data)

def normalize(url):
 try:
  p=urlsplit(urldefrag(url)[0]);port=p.port
  if p.scheme!='https' or not p.hostname or p.username or p.password or port not in (None,443):return None
  return urlunsplit(('https',p.hostname.lower(),re.sub('/+','/',p.path or '/'),p.query,''))
 except ValueError:return None

def allowed(url,cfg):
 p=urlsplit(url)
 if p.scheme!='https' or p.hostname not in cfg['allowed_hosts'] or p.port not in (None,443):return False
 if any(x.lower() in p.path.lower() for x in cfg.get('exclude_path_patterns',[])):return False
 if cfg.get('include_path_patterns') and not any(x.lower() in p.path.lower() for x in cfg['include_path_patterns']):return False
 return not p.path.lower().endswith(SKIP_EXT)

class RestrictedRedirect(HTTPRedirectHandler):
 def __init__(self,cfg):self.cfg=cfg
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  target=normalize(newurl)
  if not target or not allowed(target,self.cfg):raise ValueError('Blocked redirect outside allowed HTTPS hosts: '+newurl[:180])
  return super().redirect_request(req,fp,code,msg,headers,target)

class Fetcher:
 def __init__(self,cfg,insecure=False):
  self.cfg=cfg;self.insecure=insecure;self.last={};self.retry_count=0
  ctx=ssl.create_default_context()
  if cfg.get('ca_bundle'):ctx.load_verify_locations(cafile=str((ROOT/cfg['ca_bundle']).resolve()))
  if insecure:
   # Only user-configured hosts can be fetched, including redirects. Never change global SSL context.
   ctx.check_hostname=False;ctx.verify_mode=ssl.CERT_NONE
  self.opener=build_opener(HTTPSHandler(context=ctx),RestrictedRedirect(cfg))
 def fetch(self,url,accept='text/html',limit=None):
  if not allowed(url,self.cfg):raise ValueError('URL not in allowlist')
  host=urlsplit(url).hostname;tries=self.cfg['retries']+1
  for attempt in range(tries):
   wait=self.cfg['delay_seconds']-(time.monotonic()-self.last.get(host,0))
   if wait>0:time.sleep(wait)
   self.last[host]=time.monotonic()
   try:
    req=Request(url,headers={'User-Agent':self.cfg['user_agent'],'Accept':accept})
    with self.opener.open(req,timeout=self.cfg['timeout_seconds']) as r:
     final=normalize(r.url)
     if not final or not allowed(final,self.cfg):raise ValueError('Disallowed final URL')
     n=limit or self.cfg['max_response_bytes'];raw=r.read(n+1)
     if len(raw)>n:raise ValueError('Response exceeds configured byte limit')
     return final,raw,r.headers.get_content_type(),r.headers.get_content_charset()
   except HTTPError as e:
    if e.code not in (408,429,500,502,503,504) or attempt==tries-1:raise
    retry_after=e.headers.get('Retry-After','')
    try:backoff=min(30,max(1,int(retry_after)))
    except ValueError:backoff=min(15,2**attempt)
   except (URLError,TimeoutError,ConnectionError) as e:
    if attempt==tries-1:raise
    backoff=min(15,2**attempt)
   self.retry_count+=1;print(f'[RETRY] {attempt+1}/{tries-1} {url}',flush=True)
   time.sleep(backoff)
  raise RuntimeError('unreachable')

class Robots:
 def __init__(self,fetcher,errors):self.fetcher=fetcher;self.errors=errors;self.cache={}
 def can_fetch(self,url):
  p=urlsplit(url);host=p.netloc
  if host not in self.cache:
   robots_url=f'https://{host}/robots.txt'
   try:
    _,body,typ,_=self.fetcher.fetch(robots_url,'text/plain',500000)
    rp=RobotFileParser();rp.parse(body.decode('utf-8',errors='replace').splitlines());self.cache[host]=rp
    print('[ROBOTS] Loaded',robots_url,flush=True)
   except HTTPError as e:
    if e.code in (404,410):
     rp=RobotFileParser();rp.parse([]);self.cache[host]=rp
     self.errors.append({'url':robots_url,'type':'robots_not_found','error':f'HTTP {e.code}; no robots rules published'})
    else:
     self.cache[host]=None;self.errors.append({'url':robots_url,'type':'robots_http_error','error':f'HTTP {e.code}; fail closed'})
   except Exception as e:
    kind='ssl_certificate_error' if 'CERTIFICATE_VERIFY_FAILED' in str(e) or 'certificate has expired' in str(e) else 'robots_network_error'
    self.cache[host]=None;self.errors.append({'url':robots_url,'type':kind,'error':str(e)[:350]+'; fail closed'})
    print('[ROBOTS ERROR]',kind,str(e)[:180],flush=True)
  rp=self.cache[host]
  return rp is not None and rp.can_fetch(self.fetcher.cfg['user_agent'],url)

def pdf_text(raw,max_chars):
 from pypdf import PdfReader
 reader=PdfReader(io.BytesIO(raw),strict=False)
 if reader.is_encrypted:raise ValueError('Encrypted PDF')
 chunks=[];total=0
 for page in reader.pages[:120]:
  t=page.extract_text() or ''
  chunks.append(t);total+=len(t)
  if total>=max_chars:break
 return '\n'.join(chunks)[:max_chars],len(reader.pages)

def run(cfg,insecure=False):
 cfg=dict(cfg);cfg['allowed_hosts']=[str(x).lower() for x in cfg['allowed_hosts']]
 cfg['max_pages']=min(500,max(1,int(cfg.get('max_pages',100))))
 cfg['max_documents']=min(100,max(0,int(cfg.get('max_documents',30))))
 cfg['max_depth']=min(6,max(0,int(cfg.get('max_depth',2))))
 cfg['delay_seconds']=max(1.0,float(cfg.get('delay_seconds',1.5)))
 cfg['timeout_seconds']=max(2,min(45,int(cfg.get('timeout_seconds',12))))
 cfg['max_response_bytes']=min(5000000,max(10000,int(cfg.get('max_response_bytes',2000000))))
 cfg['max_pdf_bytes']=min(15000000,max(100000,int(cfg.get('max_pdf_bytes',8000000))))
 cfg['max_text_chars']=min(60000,max(1000,int(cfg.get('max_text_chars',16000))))
 cfg['retries']=min(5,max(0,int(cfg.get('retries',2))))
 cfg['user_agent']=str(cfg.get('user_agent','MiniCampusAssistantResearchBot/1.0'))
 output=ROOT/Path(cfg.get('output_file','school-crawl-data.json')).name
 if output.name in ('additional_regulations.json','school-ui-config.json','school-crawl-config.json'):raise ValueError('Refusing to overwrite configuration')
 if insecure:print('[WARNING] TLS certificate verification DISABLED for allowlisted school hosts only. Development use only.',flush=True)
 fetcher=Fetcher(cfg,insecure);errors=[];robots=Robots(fetcher,errors)
 records=[];documents=[];links={};seen=set();q=collections.deque((normalize(u),0) for u in cfg['start_urls'])
 while q and len(records)<cfg['max_pages']:
  url,depth=q.popleft()
  if not url or url in seen or not allowed(url,cfg):continue
  seen.add(url)
  if not robots.can_fetch(url):continue
  try:
   final,raw,typ,charset=fetcher.fetch(url,'text/html,application/xhtml+xml')
   if typ not in ('text/html','application/xhtml+xml'):raise ValueError('Non-HTML response: '+str(typ))
   page=Page();page.feed(raw.decode(charset or 'utf-8',errors='replace'))
   title=' '.join(''.join(page.title).split())[:200]
   body='\n'.join(x.strip() for x in ''.join(page.text).splitlines() if x.strip())
   body=re.sub(r'\n{3,}','\n\n',html.unescape(body))[:cfg['max_text_chars']]
   if len(body)>=30:records.append({'id':f'page-{len(records)+1}','title':title,'url':final,'text':body,'retrieved_at':NOW(),'depth':depth,'source_type':'public_school_webpage'})
   if depth<cfg['max_depth']:
    for href in page.links:
     nxt=normalize(urljoin(final,href))
     if not nxt or not allowed(nxt,cfg):continue
     if urlsplit(nxt).path.lower().endswith(DOC_EXT):links[nxt]={'url':nxt,'type':'linked_document','discovered_on':final}
     elif nxt not in seen:q.append((nxt,depth+1))
   print(f'[PAGE {len(records)}/{cfg["max_pages"]}] {title[:48]} {final}',flush=True)
  except Exception as e:errors.append({'url':url,'type':'page_error','error':str(e)[:300]})
 for url,info in list(links.items()):
  row=dict(info);row['status']='not_extracted'
  if not urlsplit(url).path.lower().endswith('.pdf'):
   row['status']='unsupported_document_type';documents.append(row);continue
  if len([d for d in documents if d.get('status') in ('extracted','no_extractable_text')])>=cfg['max_documents']:
   row['status']='document_limit_reached';documents.append(row);continue
  if not robots.can_fetch(url):row['status']='blocked_by_robots';documents.append(row);continue
  try:
   final,raw,typ,_=fetcher.fetch(url,'application/pdf',cfg['max_pdf_bytes'])
   if not raw.startswith(b'%PDF-'):raise ValueError('Response is not a PDF')
   body,pages=pdf_text(raw,cfg['max_text_chars'])
   row.update({'status':'extracted' if body.strip() else 'no_extractable_text','pages':pages,'retrieved_at':NOW(),'url':final})
   if body.strip():
    records.append({'id':f'pdf-{len(records)+1}','title':Path(urlsplit(final).path).name,'url':final,'text':body,'retrieved_at':NOW(),'depth':None,'source_type':'public_school_pdf','page_count':pages})
   print(f'[PDF] {row["status"]}: {final}',flush=True)
  except Exception as e:
   row['status']='download_or_extract_error';row['error']=str(e)[:250];errors.append({'url':url,'type':'pdf_error','error':str(e)[:300]})
  documents.append(row)
 result={'school_website':cfg['start_urls'][0],'generated_at':NOW(),'crawl_policy':{'max_pages':cfg['max_pages'],'max_documents':cfg['max_documents'],'max_depth':cfg['max_depth'],'robots_respected':True,'insecure_school_ssl':insecure,'retries':cfg['retries'],'retry_count':fetcher.retry_count,'pdf_text_extraction':True},'records':records,'document_links':documents,'errors':errors[:200]}
 output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 print(f'Wrote {len(records)} searchable records, {len(documents)} document links, {len(errors)} errors to {output}',flush=True)
 return result

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--config',default='school-crawl-config.json');ap.add_argument('--max-pages',type=int)
 ap.add_argument('--max-documents',type=int);ap.add_argument('--insecure-school-ssl',action='store_true',help='DEV ONLY: skip TLS validation for configured school hosts')
 args=ap.parse_args();cfg=json.loads((ROOT/args.config).read_text(encoding='utf-8'))
 if args.max_pages is not None:cfg['max_pages']=args.max_pages
 if args.max_documents is not None:cfg['max_documents']=args.max_documents
 run(cfg,args.insecure_school_ssl)
if __name__=='__main__':main()
