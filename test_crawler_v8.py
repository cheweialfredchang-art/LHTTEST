import io,unittest
from pathlib import Path
from importlib.machinery import SourceFileLoader
from pypdf import PdfWriter
m=SourceFileLoader('crawler_v8',str(Path(__file__).with_name('school-crawler.py'))).load_module()
class TestV8(unittest.TestCase):
 def setUp(self):self.cfg={'allowed_hosts':['www.ykvs.ntpc.edu.tw'],'exclude_path_patterns':[],'include_path_patterns':[]}
 def test_urls(self):
  self.assertTrue(m.allowed('https://www.ykvs.ntpc.edu.tw/a.pdf',self.cfg))
  self.assertFalse(m.allowed('https://evil.test/a.pdf',self.cfg))
  self.assertIsNone(m.normalize('http://www.ykvs.ntpc.edu.tw/'))
 def test_redirect_block(self):
  from urllib.request import Request
  with self.assertRaises(ValueError):m.RestrictedRedirect(self.cfg).redirect_request(Request('https://www.ykvs.ntpc.edu.tw/'),None,302,'redirect',{},'https://evil.test/')
 def test_pdf(self):
  writer=PdfWriter();writer.add_blank_page(width=100,height=100);buf=io.BytesIO();writer.write(buf)
  text,pages=m.pdf_text(buf.getvalue(),1000);self.assertEqual(pages,1);self.assertEqual(text,'')
 def test_robots(self):
  class Fake:
   cfg={'user_agent':'MiniCampusAssistantResearchBot/1.0'}
   def fetch(self,url,*args):return url,b'User-agent: *\nDisallow: /private\n','text/plain','utf-8'
  r=m.Robots(Fake(),[]);self.assertTrue(r.can_fetch('https://www.ykvs.ntpc.edu.tw/'));self.assertFalse(r.can_fetch('https://www.ykvs.ntpc.edu.tw/private'))
if __name__=='__main__':unittest.main()
