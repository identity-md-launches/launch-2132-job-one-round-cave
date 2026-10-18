# Catalog Delta

Catalog Delta compares two finite dependency catalogs and reports changed root
constraints, available releases, release labels and dependency constraints. It
helps a worker review a catalog update before attempting another resolution.
It uses Python 3.9+ and the standard library, validates both files with the existing
Offline Resolver grammar, and does not resolve, install, download or modify
packages. Run it from the repository root.

One command shows it working against two committed finite projections of public
Requests metadata:

```sh
python3 -B line-4/tools/catalog-delta/delta.py demo
```

I ran that command here. It compared the Requests 2.32.5 catalog with the
separate conflict example containing Requests 2.25.1. The report found changed
root constraints and three added releases: `chardet` 4.0.0, `idna` 2.10 and
`requests` 2.25.1. It found no changed dependency maps for shared releases and
emitted normalized SHA-256 digests for both inputs. These snapshots have
different illustrative roots; the report makes no claim that one is a later
registry state.

For your own workspace-local catalogs:

```sh
python3 -B line-4/tools/catalog-delta/delta.py before.json after.json
```

The output lists exact before/after root strings and dependency maps, and
counts packages and releases added or removed. Numeric-equivalent release labels
such as `1` and `1.0` are paired and shown as a label change. Package aliases
are canonicalized by the inherited resolver. Digests ignore JSON whitespace and
object order but bind the normalized roots, package names, release labels and
dependency strings. Both inputs must use the resolver's finite numeric-version
and conjunctive-constraint grammar; paths must remain inside the current
workspace and files are limited by the inherited 1 MB loader.

Exit 0 means a comparison completed; exit 2 means an input or read error. A
catalog delta does not say whether a selection is compatible, whether a solution
exists, whether metadata is current, or whether a package artifact or publisher
is trustworthy. Run Offline Resolver or Joint Check separately for compatibility.
The comparison reuses Offline Resolver validation and path handling, so those
remain trust dependencies rather than independent checks.
