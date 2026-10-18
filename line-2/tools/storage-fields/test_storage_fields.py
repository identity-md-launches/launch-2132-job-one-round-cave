import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('tested_storage_fields', HERE / 'storage_fields.py')
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)
w = t.w


class StorageFieldsTests(unittest.TestCase):
    def setUp(self):
        self.bundle = w.load_bundle(HERE.parent / 'state-witness/examples/zto-pool-mainnet.json')
        self.layout = t.load_layout(HERE / 'pool-layout.json')

    def verify(self):
        return t.verify(self.bundle, w.DEMO_ROOT, w.POOL_MANAGER, self.layout)

    def test_real_pool(self):
        result = self.verify()
        self.assertTrue(result['verified'])
        fields = {f['name']: f['valueDecimal'] for f in result['slots'][0]['fields']}
        self.assertEqual(fields, {'sqrtPriceX96': '20794297345123442418062648917057',
                                 'tick': '111407', 'protocolFee0To1': '0',
                                 'protocolFee1To0': '0', 'lpFee': '12500'})
        self.assertTrue(result['slots'][0]['storageExists'])
        self.assertEqual(result['slots'][0]['unusedBits'], '0x0')

    def test_wrong_root_fails_before_decoding(self):
        with patch.object(t, 'decode_word', side_effect=AssertionError('decode called')):
            with self.assertRaises(w.Invalid):
                t.verify(self.bundle, '0x' + '11'*32, w.POOL_MANAGER, self.layout)

    def test_wrong_account(self):
        with self.assertRaises(w.Invalid):
            t.verify(self.bundle, w.DEMO_ROOT, w.ZTO, self.layout)

    def test_forged_value_fails(self):
        self.bundle['proof']['storageProof'][0]['value'] = '0x1'
        with self.assertRaises(w.Invalid):
            self.verify()

    def test_missing_nodes_fail(self):
        self.bundle['proof']['storageProof'][0]['proof'] = []
        with self.assertRaises(w.Invalid):
            self.verify()

    def test_wrong_slot(self):
        self.layout['slots'][0]['slot'] = '0x1'
        with self.assertRaises(w.Invalid):
            self.verify()

    def test_overlapping_fields_fail(self):
        self.layout['slots'][0]['fields'][1]['offset'] = 159
        with self.assertRaises(w.Invalid):
            self.verify()

    def test_duplicate_names_and_numeric_slots(self):
        for kind in ('name', 'slot'):
            with self.subTest(kind=kind):
                layout = copy.deepcopy(self.layout)
                if kind == 'name':
                    layout['slots'][0]['fields'][1]['name'] = 'sqrtPriceX96'
                else:
                    layout['slots'].append(copy.deepcopy(layout['slots'][0]))
                    layout['slots'][1]['slot'] = layout['slots'][1]['slot'].upper().replace('0X', '0x')
                with self.assertRaises(w.Invalid):
                    t.validate_layout(layout)

    def test_bad_boundaries_types_unknown_keys(self):
        for key, value in [('offset', -1), ('offset', 256), ('offset', True),
                           ('bits', 0), ('bits', 257), ('bits', 1.5),
                           ('signed', 1), ('name', ''), ('name', 'x\ny'), ('typo', 1)]:
            with self.subTest(key=key, value=value):
                layout = copy.deepcopy(self.layout)
                layout['slots'][0]['fields'][0][key] = value
                with self.assertRaises(w.Invalid):
                    t.validate_layout(layout)

    def test_signed_extremes_and_lsb_offsets(self):
        # Artificial arithmetic vectors only, never represented as chain evidence.
        for width in (1, 8, 24, 128, 256):
            row = {'slot': '0x1', 'requireUnusedZero': True,
                   'fields': [{'name': 'v', 'offset': 256-width, 'bits': width, 'signed': True}]}
            for expected in (-(1 << (width-1)), -1, 0, (1 << (width-1))-1):
                word = (expected % (1 << width)) << (256-width)
                self.assertEqual(t.decode_word(word, row)['fields'][0]['valueDecimal'], str(expected))

    def test_unused_bits_reject_or_report(self):
        self.layout['slots'][0]['fields'].pop()  # omit nonzero LP fee
        with self.assertRaises(w.Invalid):
            self.verify()
        self.layout['slots'][0]['requireUnusedZero'] = False
        self.assertNotEqual(self.verify()['slots'][0]['unusedBits'], '0x0')

    def test_proven_absence_reports_zero(self):
        bundle = w.load_bundle(HERE.parent / 'state-witness/examples/zto-mainnet.json')
        layout = {'format': 'storage-fields/1', 'slots': [
            {'slot': hex(i), 'requireUnusedZero': True, 'fields': [
                {'name': 'raw'+str(i), 'offset': 0, 'bits': 256, 'signed': False}]} for i in range(2)]}
        result = t.verify(bundle, w.DEMO_ROOT, w.ZTO, layout)
        self.assertEqual([r['storageExists'] for r in result['slots']], [False, False])
        self.assertEqual([r['fields'][0]['valueDecimal'] for r in result['slots']], ['0', '0'])

    def test_fingerprint_normalizes_order_and_hex(self):
        original = self.verify()['layoutSha256']
        self.layout['slots'][0]['fields'].reverse()
        self.layout['slots'][0]['slot'] = self.layout['slots'][0]['slot'].upper().replace('0X', '0x')
        self.assertEqual(self.verify()['layoutSha256'], original)
        self.layout['slots'][0]['fields'][0]['signed'] = True
        self.assertNotEqual(self.verify()['layoutSha256'], original)

    def test_metadata_is_not_evidence_and_inputs_unchanged(self):
        self.bundle['block'] = {'stateRoot': 'forged', 'number': 'latest'}
        original = copy.deepcopy((self.bundle, self.layout))
        report = self.verify()
        self.assertEqual((self.bundle, self.layout), original)
        self.assertNotIn('latest', json.dumps(report))
        self.assertEqual(report['stateRoot'], w.DEMO_ROOT)

    def test_strict_json_and_workspace_boundary(self):
        with self.assertRaises(w.Invalid):
            w.parse_json('{"format":"a","format":"b"}')
        with self.assertRaises(w.Invalid):
            t.load_layout(Path.cwd().parent / 'forbidden-layout.json')

    def test_cli_success_and_failure(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(t.main(['demo']), 0)
        self.assertTrue(json.loads(out.getvalue())['verified'])
        self.assertEqual(err.getvalue(), '')
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(t.main(['verify', str(HERE.parent / 'state-witness/examples/zto-pool-mainnet.json'),
                                     str(HERE / 'pool-layout.json'), '--state-root', w.DEMO_ROOT,
                                     '--address', w.ZTO]), 1)
        self.assertEqual(out.getvalue(), '')
        self.assertFalse(json.loads(err.getvalue())['verified'])


if __name__ == '__main__':
    unittest.main()
