#!/usr/bin/env python3
"""Verify a storage witness before extracting caller-specified packed fields."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('storage_fields_witness', HERE.parent / 'state-witness/witness.py')
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)
UINT256 = (1 << 256) - 1


def validate_layout(layout):
    """Return normalized layout. Offsets count bits from the least significant bit."""
    w.require(isinstance(layout, dict) and set(layout) == {'format', 'slots'},
              'layout must contain exactly format and slots')
    w.require(layout['format'] == 'storage-fields/1', 'unsupported layout format')
    slots = layout['slots']
    w.require(isinstance(slots, list) and 1 <= len(slots) <= 64, 'layout requires 1..64 slots')
    seen_slots, names, normalized = set(), set(), []
    for row in slots:
        w.require(isinstance(row, dict) and set(row) == {'slot', 'fields', 'requireUnusedZero'},
                  'slot requires exactly slot, fields, requireUnusedZero')
        slot = w.slot_number(row['slot'])
        w.require(slot not in seen_slots, 'duplicate layout slot')
        seen_slots.add(slot)
        w.require(type(row['requireUnusedZero']) is bool, 'requireUnusedZero must be boolean')
        fields = row['fields']
        w.require(isinstance(fields, list) and 1 <= len(fields) <= 32, 'slot requires 1..32 fields')
        mask, clean = 0, []
        for field in fields:
            w.require(isinstance(field, dict) and set(field) == {'name', 'offset', 'bits', 'signed'},
                      'field requires exactly name, offset, bits, signed')
            name, offset, bits, signed = (field[k] for k in ('name', 'offset', 'bits', 'signed'))
            w.require(isinstance(name, str) and re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,63}', name) is not None,
                      'field name must be a bounded ASCII identifier')
            w.require(name not in names, 'duplicate field name')
            names.add(name)
            w.require(type(offset) is int and type(bits) is int and 0 <= offset < 256
                      and 1 <= bits <= 256 and offset + bits <= 256, 'field exceeds storage word')
            w.require(type(signed) is bool, 'signed must be boolean')
            part = ((1 << bits) - 1) << offset
            w.require(mask & part == 0, 'overlapping fields')
            mask |= part
            clean.append(dict(field))
        normalized.append({'slot': hex(slot), 'fields': sorted(clean, key=lambda f: f['offset']),
                           'requireUnusedZero': row['requireUnusedZero']})
    return {'format': 'storage-fields/1', 'slots': sorted(normalized, key=lambda s: int(s['slot'], 16))}


def decode_word(word, row):
    """Internal decoding only: this function alone does NOT verify a proof."""
    w.require(type(word) is int and 0 <= word <= UINT256, 'word must be uint256')
    mask, fields = 0, []
    for field in row['fields']:
        bits, offset = field['bits'], field['offset']
        raw = (word >> offset) & ((1 << bits) - 1)
        value = raw - (1 << bits) if field['signed'] and raw & (1 << (bits - 1)) else raw
        mask |= ((1 << bits) - 1) << offset
        fields.append({**field, 'rawBits': hex(raw), 'valueDecimal': str(value)})
    unused = word & (UINT256 ^ mask)
    w.require(not row['requireUnusedZero'] or unused == 0, 'nonzero unused bits violate caller layout')
    return {'slot': row['slot'], 'word': '0x' + word.to_bytes(32, 'big').hex(),
            'unusedBits': hex(unused), 'fields': fields}


def verify(bundle, state_root, address, layout):
    normalized = validate_layout(layout)
    canonical = json.dumps(normalized, sort_keys=True, separators=(',', ':')).encode('ascii')
    w.require(isinstance(bundle, dict) and bundle.get('format') == 'state-witness/1', 'unsupported witness format')
    state = w.verify(bundle.get('proof'), state_root, address,
                     [row['slot'] for row in normalized['slots']])
    w.require(state['accountExists'], 'contract account is absent')
    # No unverified claim or bundle metadata enters field decoding.
    words = {row['slot']: row for row in state['storage']}
    decoded = []
    for row in normalized['slots']:
        proven = words[row['slot']]
        decoded.append({**decode_word(int(proven['value'], 16), row), 'storageExists': proven['exists']})
    return {'verified': True, 'format': 'storage-fields-result/1',
            'stateRoot': state['stateRoot'], 'address': state['address'],
            'codeHash': state['codeHash'], 'layoutSha256': hashlib.sha256(canonical).hexdigest(),
            'slots': decoded,
            'trust': 'Raw words are proven against the supplied root. Authenticate the root independently. Field names, offsets, signedness and meaning are caller assumptions, not facts established by a proof. No price, balance, consensus, finality or current-state claim is made.'}


def load_layout(path):
    with w.workspace_path(path).open('rb') as stream:
        raw = stream.read(65537)
    w.require(len(raw) <= 65536, 'layout exceeds 64 KiB')
    return validate_layout(w.parse_json(raw))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('demo', help='verify and extract the historical real ZTO/IMD pool fields offline')
    check = sub.add_parser('verify')
    check.add_argument('witness')
    check.add_argument('layout', help='caller-reviewed storage-fields/1 JSON')
    check.add_argument('--state-root', required=True)
    check.add_argument('--address', required=True)
    args = parser.parse_args(argv)
    try:
        demo = args.command == 'demo'
        bundle = w.load_bundle(HERE.parent / 'state-witness/examples/zto-pool-mainnet.json' if demo else args.witness)
        layout = load_layout(HERE / 'pool-layout.json' if demo else args.layout)
        result = verify(bundle, w.DEMO_ROOT if demo else args.state_root,
                        w.POOL_MANAGER if demo else args.address, layout)
        if demo:
            result['demo'] = 'Real ZTO/IMD historical fixture at block 26212390; illustrative RPC-observed root, not an independently authenticated checkpoint.'
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except w.Invalid as error:
        print(json.dumps({'verified': False, 'error': str(error)}), file=sys.stderr)
        return 1
    except (OSError, ValueError, TypeError, KeyError, RecursionError):
        print(json.dumps({'verified': False, 'error': 'Unreadable or malformed input.'}), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
