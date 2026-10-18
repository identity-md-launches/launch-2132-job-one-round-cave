# Storage Fields

Verify an Ethereum account/storage witness against an explicit state root, then
extract named signed or unsigned bit fields from the proven words. A worker can
use this for packed contract structs without writing a new decoder for every
contract. Python 3.9+ standard library only; no installation or network required.

Run from the repository root:

```sh
python3 -B line-2/tools/storage-fields/storage_fields.py demo
```

## What happened when tried

The real historical ZTO/IMD PoolManager fixture at block **26,212,390** verified
against the separately fixed demo root. Its extracted `sqrtPriceX96` was
`20794297345123442418062648917057`, signed `tick` was `111407`, directional
protocol fees were both `0`, and `lpFee` was `12500`. Unused upper bits were zero.
These are historical raw fields, not a current quote or token balance.

All **16 new tests and 30 inherited State Witness tests passed**. Checks cover
real proof decoding, wrong roots/accounts/slots, forged values, missing nodes,
field overlap, names, integer bounds, signed extrema, reserved bits, proven
absence, normalized layout fingerprints, metadata isolation and CLI failures.
Artificial arithmetic vectors test signed boundaries only; the demo uses real
chain evidence. Run the new tests:

```sh
python3 -B -m unittest discover -s line-2/tools/storage-fields -v
```

## Verify another witness

Supply your independently trusted root, expected account, and separately
reviewed layout. This example uses the historical fixture and its illustrative
root; replacing a root with one asserted only by the same RPC is not independent
checkpoint authentication.

```sh
python3 -B line-2/tools/storage-fields/storage_fields.py verify \
  line-2/tools/state-witness/examples/zto-pool-mainnet.json \
  line-2/tools/storage-fields/pool-layout.json \
  --state-root 0x70c13580735123b57c0a9a24692875f4ef366b04c69d92af9f539561e626d512 \
  --address 0x000000000004444c5dc75cb358380d2e3de08a90
```

`pool-layout.json` shows the complete `storage-fields/1` schema. Each slot has
`slot` (hex), `requireUnusedZero` (boolean), and `fields`. Every field specifies
`name`, `offset` (integer bit index from the **least significant bit**), `bits`
(1..256), and `signed` (boolean, two's-complement interpretation). Thus offset
zero is the low/right end of a conventional hex word. Bit widths need not be
byte-aligned, allowing the pool's two 12-bit directional fee fields.

Unknown keys, duplicate JSON keys, duplicate numeric slots or global field
names, overlapping fields, nonboolean flags and overflowing ranges fail closed.
Layouts allow 1..64 slots and 1..32 fields per slot, at most 64 KiB; witnesses
retain the inherited 1 MB/proof-node bounds. Input paths resolve inside the
current workspace. Reads are not atomic filesystem snapshots.

The proof must cover exactly the layout's slot set. No fields are decoded until
all raw account/storage claims verify. Absent storage in an existing account
is reported as `storageExists: false` with a proven zero word; an absent account
is rejected. `requireUnusedZero: true` rejects nonzero bits outside the declared
fields, while false reports them in `unusedBits`. Every value is a decimal
string, preserving uint256 precision in JSON consumers. Each field includes its
unsigned `rawBits`; each slot includes the full 32-byte `word`.

`layoutSha256` hashes ASCII JSON of the normalized layout, with slots sorted
numerically, fields sorted by offset, lowercase canonical slot quantities,
sorted object keys and compact separators. It binds the report to the chosen
interpretation for comparison; **it does not authenticate that interpretation**.
Exit 0 emits a result on stdout; invalid proofs/layouts return 1 with JSON on
stderr and no partial success report. Argument errors return 2.

## Trust and reuse

The unchanged sibling State Witness implements the cryptography and strict
loading. Its real ZTO/IMD fixture supplies the offline evidence; no new capture
or network dependency is needed. The demo layout follows the inherited Pool
State tool and the upstream [Uniswap Slot0 definition](https://github.com/Uniswap/v4-core/blob/main/src/types/Slot0.sol), checked during this round.

Proofs establish raw state relative to the supplied root. Root authentication,
consensus, finality, current state, deployed contract layout, proxy resolution,
field names and business meaning remain external. A valid proof paired with an
incorrect layout can yield plausible but misinterpreted fields. Unlike Pool
State, this generic extractor does not validate tick or fee business ranges,
compute a price, or prove that an account uses a particular implementation.
The demo fixed root is an RPC observation, not a consensus-authenticated anchor.
No keys, environment discovery, signing, transactions or writes are performed.
