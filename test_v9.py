import unittest,json,subprocess
from pathlib import Path
from school_crawl_search import search_pages,expand_query,split_chunks
ROOT=Path(__file__).resolve().parent
import importlib.util
spec=importlib.util.spec_from_file_location('crawl_diff_v9',ROOT/'crawl-diff-v9.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
diff=mod.diff
ROOT=Path(__file__).resolve().parent
class V9Tests(unittest.TestCase):
 def test_uploaded_data(self):
  d=json.loads((ROOT/'school-crawl-data.json').read_text(encoding='utf-8'));self.assertEqual(len(d['records']),150)
 def test_query_expansion(self):self.assertIn('重修',expand_query('被當怎麼辦'))
 def test_search_credit(self):self.assertTrue(search_pages('重補修')['matches'])
 def test_citation(self):self.assertTrue(all(x['url'].startswith('https://www.ykvs.ntpc.edu.tw/') for x in search_pages('請假')['matches']))
 def test_chunk(self):self.assertTrue(split_chunks('測試'*500))
 def test_diff(self):self.assertEqual(diff({'records':[{'url':'a','text':'old'}]},{'records':[{'url':'a','text':'new'}]})['changed'],['a'])
 def test_100_cases(self):self.assertEqual(len(json.loads((ROOT/'evaluation-100-v9.json').read_text(encoding='utf-8'))['cases']),100)
 def test_no_pdf_claim(self):
  d=json.loads((ROOT/'school-crawl-data.json').read_text(encoding='utf-8'));self.assertEqual(sum(r.get('source_type')=='public_school_pdf' for r in d['records']),0)
if __name__=='__main__':unittest.main()
