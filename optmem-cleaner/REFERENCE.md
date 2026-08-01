# optmem-cleaner reference

Disclosed reference for `SKILL.md`. Load it when a step needs store formats, size limits, or tool behaviour.

## Store layout

- `LOG.txt` — append-only raw log. Fixed-width records, 320 bytes each: `#<id> YYYY-MM-DD <text>` padded with spaces. Position is identity: memory id `i` lives at byte offset `i * 320`.
- `TREE/<size>` — one file per block size (2, 4, 8, ...). Fixed-width records, 288 bytes each, one per block in order: record `k` of file `<size>` holds the summary of block `[k*size, (k+1)*size)`, stored as plain padded text (no id prefix).
- `config` — optional size overrides. `ENTRY_CHARS` (default 280) is the byte limit per memory; `WAKE_LINES`, `PART_CHARS`, `PART_LINES` affect display only.

## Tool behaviour (memo)

- One memory is one line of at most `ENTRY_CHARS` bytes (default 280).
- `memo note` stamps the current date automatically; there is no way to pass a date to `note`.
- `memo import <file>` accepts lines `YYYY-MM-DD <text>`. It validates every line first (UTF-8, real date, dates non-decreasing, non-empty, ≤ `ENTRY_CHARS`) and then appends all records atomically under a lock. Any violation aborts the whole import before anything is written.
- `memo nap` compresses one pending block per call, in order; the summary is written by hand, not by the tool.
- `memo wake` prints raw entries while the store fits in `WAKE_LINES`; beyond that it needs tree summaries and refuses until the pending compressions are done.
- `memo recall` searches the raw log but caps its output; it is not a complete export.

## Script

`scripts/optmem_cleaner.py` (Python 3, standard library only):

- `export --memory-dir <dir> [-o FILE]` — prints every raw record as `#<id> <date> <text>` and every summary as `SUMMARY #<lo>-<hi> <text>`, then prints counts to stderr.
- `check FILE --memory-dir <dir>` — validates an import file against the same rules as `memo import` (including the store's `ENTRY_CHARS` override) and prints a summary. Exit code 0 only when the file is valid and non-empty.

## Restore

- Git-tracked store: `git checkout <backup commit> -- <memory store paths>`.
- Copied store: copy the files from `optmem-clean-YYYYMMDD/backup/` back into the memory directory.

After either restore, run `memo nap` until nothing is left, then `memo wake` once.
