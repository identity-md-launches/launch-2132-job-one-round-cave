#!/usr/bin/env python3
"""Regenerate a finite-catalog delta and search its exact report lines offline."""
import argparse
import json
from pathlib import Path
import sys

import delta
import search

HERE = Path(__file__).resolve().parent


def quoted(value):
    # Keep user-controlled constraints on one physical source line.
    return json.dumps(value, ensure_ascii=True, sort_keys=True)


def document(result):
    rows = [
        '# Finite catalog comparison',
        'Before normalized SHA-256: ' + result['before_sha256'],
        'After normalized SHA-256: ' + result['after_sha256'],
        'Scope: supplied snapshots only; no compatibility, freshness or trust claim.',
        'Snapshot order is caller-selected, not inferred chronological order.',
        '',
    ]
    for item in result['root_changes']:
        rows.append('Root ' + item['package'] + ': before ' + quoted(item['before'])
                    + '; after ' + quoted(item['after']))
    for item in result['packages']:
        name = item['package']
        for label in item['releases_added']:
            rows.append('Release added: ' + name + ' ' + label)
        for label in item['releases_removed']:
            rows.append('Release removed: ' + name + ' ' + label)
        for labels in item['release_labels_changed']:
            rows.append('Release label ' + name + ': before ' + labels['before']
                        + '; after ' + labels['after'])
        for change in item['dependency_changes']:
            old, new = change['before'], change['after']
            for dep in sorted(old.keys() | new.keys()):
                if old.get(dep) != new.get(dep):
                    rows.append('Dependency ' + name + ' (' + change['release_before']
                                + ' -> ' + change['release_after'] + ') requires ' + dep
                                + ': before ' + quoted(old.get(dep))
                                + '; after ' + quoted(new.get(dep)))
    if not result['root_changes'] and not result['packages']:
        rows.append('No catalog changes.')
    rows.append('Counts: ' + quoted(result['counts']))
    return '\n'.join(rows) + '\n'


def compare(before, after, query, limit=5):
    result = delta.compare(before, after)
    text = document(result)
    source = {'path': 'catalog-delta.md', 'text': text,
              'sha256': search.digest(text.encode('utf-8'))}
    index = {'format': search.FORMAT, 'documents': [source]}
    # Recomputed report bytes, not an assertion of a live file on disk.
    hits = search.search_snapshot(index, query, limit=limit)
    return {'format': 'catalog-evidence/v1', 'delta': result,
            'documents': [source], 'search': hits,
            'trust': 'Citations bind the regenerated comparison bytes. They do not '
                     'authenticate source catalogs, compatibility or factual truth.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    demo = sub.add_parser('demo')
    demo.add_argument('query', nargs='?', default='requests idna')
    run = sub.add_parser('compare')
    run.add_argument('before')
    run.add_argument('after')
    run.add_argument('query')
    for child in (demo, run):
        child.add_argument('--limit', type=int, default=5)
    args = parser.parse_args(argv)
    try:
        before, after = ((HERE / 'examples/before.json', HERE / 'examples/after.json')
                         if args.command == 'demo' else (args.before, args.after))
        result = compare(delta.resolver.load(before), delta.resolver.load(after),
                         args.query, args.limit)
        print(json.dumps(result, indent=2, ensure_ascii=True))
        return 0 if result['search']['hits'] else 1
    except (delta.resolver.Invalid, search.SearchError, OSError, UnicodeError,
            ValueError, RecursionError) as error:
        print(json.dumps({'format': 'catalog-evidence/v1', 'error': str(error)}),
              file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
