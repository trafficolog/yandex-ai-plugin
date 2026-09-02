import base64, unittest
from scripts.ys_parse import decode_raw_data, parse_xml_results, parse_search_response
XML='''<yandexsearch><response><results><grouping>\n<group><doc><url>https://Example.com/a</url><domain>Example.com</domain><title>Title A</title><passages><passage>Snippet A</passage></passages><modtime>20260901</modtime></doc></group>\n<group><doc><url>https://b.example/path</url><title>Title B</title></doc></group>\n</grouping></results></response></yandexsearch>'''
class TestParse(unittest.TestCase):
    def test_decode_base64(self): self.assertIn('<yandexsearch>',decode_raw_data(base64.b64encode(XML.encode()).decode()))
    def test_parse_xml_tolerates_missing_optional_fields(self):
        rows=parse_xml_results(XML); self.assertEqual(len(rows),2); self.assertEqual(rows[0]['rank'],1); self.assertEqual(rows[0]['snippet'],'Snippet A'); self.assertEqual(rows[1]['rank'],2); self.assertIsNone(rows[1]['modified_at'])
    def test_parse_response_xml(self):
        out=parse_search_response({'rawData':base64.b64encode(XML.encode()).decode()},'FORMAT_XML'); self.assertEqual(out['format'],'xml'); self.assertEqual(len(out['results']),2)
    def test_html_is_raw_artifact(self):
        html='<html>ad and quick answer</html>'; out=parse_search_response({'rawData':base64.b64encode(html.encode()).decode()},'FORMAT_HTML'); self.assertEqual(out['format'],'html'); self.assertEqual(out['raw'],html); self.assertNotIn('results',out)
