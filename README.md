# optmem-cleaner

A user-invoked skill that safely cleans an [OptMem](https://github.com/VictorTaelin/OptMem) memory store. Designed and tested against OptMem at commit [`1fb164c`](https://github.com/VictorTaelin/OptMem/commit/1fb164c).

OptMem is append-only: there is no supported way to delete or reorganize memories. `optmem-cleaner` performs a supervised reset:

1. Back up the store (git commit when tracked, file copy otherwise).
2. Export every raw memory and every compressed summary.
3. Curate the full list by judgment — keep / merge / delete / rewrite, flagging anything undecided for the user — with user review at every gate.
4. Clear the store and re-import the approved list, preserving original timestamps.
5. Rebuild all compressions and verify with `wake`.

Invoke with `auto` (for example `/optmem-cleaner auto`) to skip every human check and run start to finish without stopping. All backups and files are still created along the way for later review.

## Safety

- Destructive by design: this skill clears a memory store. Every destructive step requires explicit user confirmation, and a verified backup always exists first. In auto mode the user pre-authorizes the whole run by invoking with `auto`; the verified backup is still created first.
- The cleaning itself is judgment work done by the agent: the helper script only exports and validates, never edits memory. Do not use code to deduplicate, merge, filter, or rewrite memories.
- Only the memory store is touched: `LOG.txt` and `TREE/` inside the memory directory. Nothing else.
- Parallel sessions may share the store. Confirm with the user at the very start of the run that no other session using this store is active; if they cannot confirm, stop.

## Requirements

- Python 3 (standard library only)
- The OptMem `memo` tool

## Install

Copy the `optmem-cleaner` folder into your skills directory (for example `.agents/skills/`), then invoke it by name: `$optmem-cleaner`.

## Layout

- `SKILL.md` — the procedure. Edit the "Cleaning criteria" section to change the keep / merge / delete / flag / rewrite rules.
- `scripts/optmem_cleaner.py` — read-only helpers: `export` and `check`.
- `REFERENCE.md` — store formats, size limits, and tool behaviour.
- `agents/openai.yaml` — interface metadata for OpenAI-compatible skill loaders.
