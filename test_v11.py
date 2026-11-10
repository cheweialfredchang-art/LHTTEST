import unittest,json,pathlib,subprocess,tempfile
P=pathlib.Path(__file__).parent
class TestV11(unittest.TestCase):
 def test_case_count(self):self.assertEqual(len(json.loads((P/'evaluation-cases.json').read_text(encoding="utf-8"))['cases']),120)
 def test_unique_ids(self):
  x=json.loads((P/'evaluation-cases.json').read_text(encoding="utf-8"))['cases'];self.assertEqual(len(set(c['id'] for c in x)),len(x))
 def test_unverified_gold(self):self.assertTrue(all(not c['gold_verified'] for c in json.loads((P/'evaluation-cases.json').read_text(encoding="utf-8"))['cases']))
 def test_security_count(self):self.assertEqual(len(json.loads((P/'security-cases.json').read_text(encoding="utf-8"))['cases']),10)
 def test_data_present(self):self.assertTrue((P/'school-crawl-data.json').stat().st_size>10000)
 def test_node_syntax(self):
  for f in ['server.js','trace-recorder.js','agent-v9.js']:
   with self.subTest(f=f):self.assertEqual(subprocess.run(['node','--check',str(P/f)],capture_output=True).returncode,0)
if __name__=='__main__':unittest.main()
