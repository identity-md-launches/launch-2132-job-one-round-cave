import importlib.util
import unittest
from pathlib import Path

MODULE = Path(__file__).with_name('delta.py')
spec = importlib.util.spec_from_file_location('catalog_delta', MODULE)
delta = importlib.util.module_from_spec(spec)
spec.loader.exec_module(delta)


class CatalogDeltaTests(unittest.TestCase):
    def test_release_and_root_changes(self):
        before = {'roots': {'App': '==1'}, 'packages': {
            'App': {'1': {'shared': '>=1'}}, 'shared': {'1': {}, '2': {}}}}
        after = {'roots': {'app': '==2'}, 'packages': {
            'app': {'2': {'shared': '>=2'}}, 'shared': {'1': {}, '3': {}}}}
        result = delta.compare(before, after)
        self.assertEqual(result['root_changes'], [
            {'package': 'app', 'before': '==1', 'after': '==2'}])
        packages = {p['package']: p for p in result['packages']}
        self.assertEqual(packages['app']['releases_added'], ['2'])
        self.assertEqual(packages['app']['releases_removed'], ['1'])
        self.assertEqual(packages['shared']['releases_added'], ['3'])
        self.assertEqual(packages['shared']['releases_removed'], ['2'])
        self.assertEqual(result['counts']['releases_added'], 2)
        self.assertEqual(result['counts']['releases_removed'], 2)

    def test_dependency_change_on_same_release(self):
        before = {'roots': {'app': '*'}, 'packages': {'app': {'1': {'dep': '>=1'}}}}
        after = {'roots': {'app': '*'}, 'packages': {'app': {'1.0': {'dep': '>=2'}}}}
        result = delta.compare(before, after)
        app = result['packages'][0]
        self.assertEqual(app['release_labels_changed'], [{'before': '1', 'after': '1.0'}])
        self.assertEqual(app['dependency_changes'], [{
            'release_before': '1', 'release_after': '1.0',
            'before': {'dep': '>=1'}, 'after': {'dep': '>=2'}}])
        self.assertEqual(app['releases_added'], [])
        self.assertEqual(app['releases_removed'], [])

    def test_identical_catalogs_have_no_changes_and_same_hash(self):
        data = {'roots': {'app': '>=1'}, 'packages': {'app': {'1': {}}}}
        result = delta.compare(data, data)
        self.assertEqual(result['packages'], [])
        self.assertEqual(result['root_changes'], [])
        self.assertEqual(result['before_sha256'], result['after_sha256'])

    def test_equivalent_release_labels_pair_without_dependency_delta(self):
        before = {'roots': {'app': '*'}, 'packages': {'app': {'1': {}}}}
        after = {'roots': {'app': '*'}, 'packages': {'app': {'1.0': {}}}}
        entry = delta.compare(before, after)['packages'][0]
        self.assertEqual(entry['release_labels_changed'], [{'before': '1', 'after': '1.0'}])
        self.assertEqual(entry['dependency_changes'], [])

    def test_invalid_catalog_rejected_by_inherited_grammar(self):
        bad = {'roots': {'app': '^1'}, 'packages': {'app': {'1': {}}}}
        with self.assertRaises(delta.resolver.Invalid):
            delta.compare(bad, {'roots': {'app': '*'}, 'packages': {'app': {'1': {}}}})

    def test_demo_compares_committed_real_projections(self):
        before = delta.resolver.load(
            delta.HERE.parent / 'offline-resolver/examples/requests.json')
        after = delta.resolver.load(
            delta.HERE.parent / 'conflict-core/examples/requests-conflict.json')
        result = delta.compare(before, after)
        self.assertEqual(result['status'], 'compared')
        self.assertTrue(result['root_changes'])
        self.assertIn('idna', {entry['package'] for entry in result['packages']})


if __name__ == '__main__':
    unittest.main()
