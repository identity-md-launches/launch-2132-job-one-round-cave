"""Behavioral checks for the catalog-to-citations handoff; no network."""
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import unittest

import evidence as e


class EvidenceTests(unittest.TestCase):
    def demo_inputs(self):
        return [e.delta.resolver.load(e.HERE / 'examples' / name)
                for name in ('before.json', 'after.json')]

    def test_real_snapshot_citations_are_exact(self):
        before, after = self.demo_inputs()
        result = e.compare(before, after, 'requests idna')
        self.assertEqual(result['delta']['counts']['releases_added'], 3)
        doc = result['documents'][0]
        self.assertEqual(doc['sha256'], hashlib.sha256(doc['text'].encode()).hexdigest())
        self.assertTrue(result['search']['hits'])
        for hit in result['search']['hits']:
            expected = '\n'.join(doc['text'].splitlines()[hit['line_start']-1:hit['line_end']])
            self.assertEqual(hit['text'], expected)
            self.assertEqual(hit['sha256'], doc['sha256'])
            self.assertFalse(hit['source_verified'])

    def test_recomputes_changed_constraints_and_keeps_inputs(self):
        before = {'roots': {'app': '*'}, 'packages': {'app': {'1': {'dep': '>=1'}}}}
        after = copy.deepcopy(before)
        after['packages']['app']['1']['dep'] = '>=2'
        saved = copy.deepcopy((before, after))
        result = e.compare(before, after, 'dependency')
        self.assertIn('requires dep: before ">=1"; after ">=2"', result['documents'][0]['text'])
        same = e.compare(before, before, 'catalog')
        self.assertNotEqual(result['documents'][0]['sha256'], same['documents'][0]['sha256'])
        self.assertEqual((before, after), saved)

    def test_stable_reordering(self):
        before, after = self.demo_inputs()
        reordered = {k: dict(reversed(list(v.items()))) for k, v in before.items()}
        self.assertEqual(e.compare(before, after, 'idna'), e.compare(reordered, after, 'idna'))

    def test_label_changes_and_no_changes(self):
        before = {'roots': {'app': '*'}, 'packages': {'app': {'1': {}}}}
        after = {'roots': {'app': '*'}, 'packages': {'app': {'1.0': {}}}}
        self.assertIn('Release label app: before 1; after 1.0',
                      e.compare(before, after, 'label')['documents'][0]['text'])
        self.assertIn('No catalog changes.', e.compare(before, before, 'catalog')['documents'][0]['text'])

    def test_invalid_catalog_and_query_refused(self):
        before, after = self.demo_inputs()
        invalid = copy.deepcopy(before)
        invalid['roots']['requests'] = '^2'
        with self.assertRaises(e.delta.resolver.Invalid):
            e.compare(invalid, after, 'requests')
        with self.assertRaises(e.search.SearchError):
            e.compare(before, after, '')
        with self.assertRaises(e.search.SearchError):
            e.compare(before, after, 'requests', 0)

    def test_cli_hit_miss_invalid(self):
        for args, expected in [(['demo'], 0), (['demo', 'zzznomatchzzz'], 1),
                               (['demo', '--limit', '0'], 2),
                               (['compare', '/etc/passwd', '/etc/passwd', 'root'], 2)]:
            with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
                code = e.main(args)
            self.assertEqual(code, expected)
            self.assertIsInstance(json.loads(out.getvalue() or err.getvalue()), dict)

    def test_provenance(self):
        for item in json.loads((e.HERE / 'PROVENANCE.json').read_text()):
            self.assertEqual(hashlib.sha256((e.HERE / item['copy']).read_bytes()).hexdigest(), item['copy_sha256'])
            self.assertEqual(hashlib.sha256(Path(item['source']).read_bytes()).hexdigest(), item['source_sha256'])


if __name__ == '__main__':
    unittest.main()
