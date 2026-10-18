#!/usr/bin/env python3
"""Compare two finite dependency catalogs without resolving or changing them."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = Path.cwd().resolve()
RESOLVER_PATH = HERE.parent / 'offline-resolver' / 'resolve.py'
if not RESOLVER_PATH.is_relative_to(ROOT):
    raise RuntimeError('run from the workspace containing line-4 tools')
_spec = importlib.util.spec_from_file_location('catalog_delta_resolver', RESOLVER_PATH)
resolver = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(resolver)


def normalized(data):
    """Validate with the resolver's grammar and return stable catalog content."""
    packages, roots = resolver.validate(data)
    stable_packages = {}
    for package in sorted(packages):
        releases = sorted(packages[package], key=resolver.version)
        stable_packages[package] = {
            release: packages[package][release] for release in releases
        }
    return {'roots': roots, 'packages': stable_packages}


def digest(catalog):
    encoded = json.dumps(catalog, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


def compare(before_data, after_data):
    """Report exact catalog changes; no package versions are selected."""
    before = normalized(before_data)
    after = normalized(after_data)
    old_roots, new_roots = before['roots'], after['roots']
    root_changes = []
    for package in sorted(old_roots.keys() | new_roots.keys()):
        old, new = old_roots.get(package), new_roots.get(package)
        if old != new:
            root_changes.append({'package': package, 'before': old, 'after': new})

    old_packages, new_packages = before['packages'], after['packages']
    changes = []
    counts = {'packages_added': 0, 'packages_removed': 0,
              'releases_added': 0, 'releases_removed': 0,
              'dependency_sets_changed': 0}
    for package in sorted(old_packages.keys() | new_packages.keys()):
        old_releases = old_packages.get(package, {})
        new_releases = new_packages.get(package, {})
        old_labels = {resolver.version(label): label for label in old_releases}
        new_labels = {resolver.version(label): label for label in new_releases}
        added = sorted((new_labels[v] for v in new_labels.keys() - old_labels.keys()),
                       key=resolver.version)
        removed = sorted((old_labels[v] for v in old_labels.keys() - new_labels.keys()),
                         key=resolver.version)
        renamed = []
        dependency_changes = []
        for number in sorted(old_labels.keys() & new_labels.keys()):
            old_label, new_label = old_labels[number], new_labels[number]
            if old_label != new_label:
                renamed.append({'before': old_label, 'after': new_label})
            old_deps, new_deps = old_releases[old_label], new_releases[new_label]
            if old_deps != new_deps:
                dependency_changes.append({'release_before': old_label,
                                           'release_after': new_label,
                                           'before': old_deps, 'after': new_deps})
        if not (added or removed or renamed or dependency_changes):
            continue
        counts['packages_added'] += int(package not in old_packages and package in new_packages)
        counts['packages_removed'] += int(package in old_packages and package not in new_packages)
        counts['releases_added'] += len(added)
        counts['releases_removed'] += len(removed)
        counts['dependency_sets_changed'] += len(dependency_changes)
        changes.append({'package': package, 'releases_added': added,
                        'releases_removed': removed, 'release_labels_changed': renamed,
                        'dependency_changes': dependency_changes})

    return {'method': 'catalog-delta-v1', 'status': 'compared',
            'before_sha256': digest(before), 'after_sha256': digest(after),
            'root_changes': root_changes, 'counts': counts, 'packages': changes,
            'scope': 'Exact roots, release labels and dependency constraints in two finite '
                     'catalogs are compared. No resolution, compatibility, registry freshness, '
                     'artifact availability or publisher trust is inferred.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('before', help='before catalog JSON and after catalog JSON, or demo')
    parser.add_argument('after', nargs='?', help='after catalog JSON')
    args = parser.parse_args(argv)
    try:
        if args.before == 'demo':
            if args.after is not None:
                raise resolver.Invalid('demo takes no second catalog')
            before_path = HERE.parent / 'offline-resolver' / 'examples' / 'requests.json'
            after_path = HERE.parent / 'conflict-core' / 'examples' / 'requests-conflict.json'
        else:
            if args.after is None:
                raise resolver.Invalid('both before and after catalog paths are required')
            before_path, after_path = args.before, args.after
        result = compare(resolver.load(before_path), resolver.load(after_path))
        code = 0
    except (resolver.Invalid, OSError, UnicodeError, json.JSONDecodeError,
            RecursionError, ValueError) as exc:
        result, code = {'status': 'invalid', 'error': str(exc)}, 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return code


if __name__ == '__main__':
    sys.exit(main())
