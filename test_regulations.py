import unittest
from regulation_search import search_regulations
class RetrievalTests(unittest.TestCase):
 def test_credit_synonyms(self):
  for q in ('重修怎麼辦','補修有什麼規定','我被當了要怎麼補學分','學分不足怎麼辦','重補修何時報名'):
   with self.subTest(q=q):
    d=search_regulations(q)
    self.assertTrue(any('學習評量補充規定' in x['title'] for x in d['matches']))
    self.assertTrue(d['matches'][0]['source_url'].startswith('https://'))
 def test_not_fabricate(self):
  d=search_regulations('重修報名截止日和費用')
  self.assertTrue(d['detail_requested'])
  self.assertNotIn('報名截止日', d['matches'][0]['content'])
 def test_exam(self):
  d=search_regulations('段考缺考可以補考嗎')
  self.assertTrue(any('補考' in x['title'] or '學習評量' in x['title'] for x in d['matches']))
if __name__=='__main__':unittest.main()
