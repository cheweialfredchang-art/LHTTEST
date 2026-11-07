import json,tempfile,unittest
from pathlib import Path
from importlib.machinery import SourceFileLoader
m=SourceFileLoader('crawler',str(Path(__file__).with_name('school-crawler.py'))).load_module()
s=SourceFileLoader('search',str(Path(__file__).with_name('school-crawl-search.py'))).load_module()
class Tests(unittest.TestCase):
 def test_url_filter(self):
  cfg={'allowed_hosts':['www.ykvs.ntpc.edu.tw'],'exclude_path_patterns':[],'include_path_patterns':[]}
  self.assertTrue(m.allowed('https://www.ykvs.ntpc.edu.tw/news',cfg))
  self.assertFalse(m.allowed('https://evil.example/path',cfg))
  self.assertFalse(m.allowed('http://www.ykvs.ntpc.edu.tw/news',cfg))
  self.assertFalse(m.allowed('https://www.ykvs.ntpc.edu.tw/x.png',cfg))
 def test_html(self):
  p=m.Page();p.feed('<title>公告</title><nav>隱藏</nav><h1>重修補修</h1><p>報名請看公告</p><a href="/news">詳情</a>')
  self.assertEqual(''.join(p.title),'公告');self.assertIn('/news',p.links)
  self.assertIn('重修補修',''.join(p.text));self.assertNotIn('隱藏',''.join(p.text))
if __name__=='__main__':unittest.main()
