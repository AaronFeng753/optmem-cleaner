---
name: optmem-cleaner
description: A user-gated procedure to back up, export, curate, clear, and re-import an OptMem memory store. Invoke with `auto` to run start to finish without stopping for human checks.
argument-hint: Invoke with `auto` to skip human checks.
disable-model-invocation: true
---

# optmem-cleaner

OptMem is append-only: the tool can add and compress, never delete or reorganize. This skill performs a supervised reset — back up the store, export everything, curate the full list by judgment, then clear and re-import the user-approved result with original timestamps preserved.

## Quality Is All You Need

Append-only is OptMem's normal state; this skill is a rare, supervised exception, not routine maintenance. Run it when memory quality is observably hurting — misleading entries, noise drowning out durable facts — never as scheduled slimming.

- The goal is a store where every entry is durable and true, not a smaller store. There is no target reduction, and a run that changes nothing is a good outcome.
- Keep is the default. Every deletion needs an affirmative reason from the Delete criteria; "old", "probably useless", and "takes space" are not reasons.
- Prefer merge or rewrite over delete whenever the underlying facts are still true: merging and rewriting preserve information, deletion destroys it.
- Size is already bounded by OptMem itself: `ENTRY_CHARS` caps every entry (280 bytes by default), `nap` folds old blocks into fixed-size tree summaries, and `wake` prints at most `WAKE_LINES` lines. The store can grow safely without any cleaner's help; what OptMem cannot do alone is expel bad memories. Improving quality is the only thing this skill adds — and all it needs to do. Never delete a still-true fact to save space.

## Safety contract

- Destructive by design. Every destructive step waits for explicit user confirmation, and a verified backup exists before the store is touched. In auto mode the user pre-authorizes the whole run by invoking with `auto`; the verified backup is still created first.
- Only the memory store is touched: `LOG.txt` and `TREE/` inside the memory directory. Nothing else.
- Parallel sessions may share the store. Confirm with the user at the very start of the run (step 0) that no other session using this store is active. If they cannot confirm, stop.
- Curation is judgment work: read the export and decide every keep / merge / delete / rewrite by hand. The helper script only exports and validates; it never edits the store, and no script may be written to deduplicate, merge, filter, or rewrite memories.

## Cleaning criteria

Present these bullets at the start of the run and let the user edit them before curation. They are the session's single source of truth for keep / merge / delete decisions; the user may also edit them directly in this file. They implement Quality, not quantity: the criteria exist to identify bad memories, not to shrink the list — an entry stays unless it positively matches a Delete bullet.

### Keep

- Keep is the default: an entry needs no justification to stay. Anything that does not positively match a Delete bullet remains in the store.
- Durable facts, decisions, preferences, and insights that are still true and useful beyond the session that produced them.
- Anything a future session would want to know about the project, the user, or its environment.
- Disproven approaches and dead ends: keep the conclusion that they failed. They stop future sessions from retrying them.

### Merge

- Merge is this skill's only form of reduction: it lowers the count without losing any fact. Prefer it over delete whenever the sources still hold true facts.
- Entries about the same topic, decision, or correction chain.
- A correction chain collapses to its final state; drop the intermediate links and note the final correction date. Exception: if the disproven belief is one a future session is likely to re-form (because it is plausible or documented somewhere), keep one short "X is not true" note.
- Multi-round progress notes about one effort: collapse into a single outcome entry.
- Near-duplicates whose complementary details belong together.
- A merged entry must preserve every still-true, non-redundant fact from its sources and keep the earliest source date.
- A merged entry must fit the store's entry size limit: read `ENTRY_CHARS` from the `config` file inside the memory directory (280 bytes when the file or key is absent). If it does not fit, trim details and keep conclusions, or split it into two entries that reference each other by date.

### Delete

- Delete is reserved for entries with zero or negative value for future sessions — content that misleads, adds noise, or duplicates. Cite the specific bullet behind every deletion.
- Content that should never have been recorded in the first place: work logs (finished tasks, commits, validations run — git history already holds these), transient state (current progress, next steps, which files are staged), and operational rules useful only for the one task that produced them.
- Work logs often smuggle facts inside them ("X was done/changed/fixed, because Y"). Extract any durable fact into a standalone entry stated as a fact, then delete the log. If the fact is recoverable from the docs, keep nothing.
- Pure status or progress logs with no durable content.
- Entries superseded by a later correction or by authoritative documentation.
- Exact or near duplicates that add nothing to the entry that remains.
- Ephemeral details that are no longer true and cannot be useful later.
- Content substantively covered by the project's own documentation (AGENTS.md, docs/, ADRs), regardless of wording.
- Entries whose value rests on an artifact that no longer exists (a deleted plan, report, or fixture file). If the entry still has standalone value once the pointer is removed, rewrite it instead of deleting it.
- Do not delete for size or age: a still-true, harmless entry stays no matter how old or minor it seems. Volume is compression's job, not this skill's.

### Flag for the user

- Default keep. List every flagged entry in `review.md` under "Needs user decision"; never silently resolve one yourself.
- Contradicting entries with no explicit correction marker: prefer the claim backed by direct testing over hearsay; if you cannot decide, flag it.
- Anything else you are unsure about.

### Rewrite

- Preserve dates: each entry keeps its original date; a merged entry keeps the earliest date and mentions later correction dates.
- Resolve old memory-id references by hand: rewrite them to dates or fold the referenced content into the text.
- The new list is chronological with fresh sequential ids. Never reuse or mechanically remap old ids.

## Talking to the user

- Never paste the full export, the full review, or any long list of memory entries into a reply. The content lives in files; the user reads files. Point them to the file instead.
- Whenever the user needs to review a file, state its complete path (working directory + archive folder + filename), not just the filename.
- Write `review.md` in fluent natural language — whatever language the user reads. Full sentences, plain wording, no terse codes or internal shorthand: a human must be able to read it top to bottom and understand every decision without decoding anything.

## Auto mode

If the invocation includes the word `auto` (for example `/optmem-cleaner auto`), run the whole procedure start to finish without stopping for any human check.

- The confirmation gates in steps 0, 5, 7, and 9 are skipped; everything else runs unchanged. The Cleaning criteria apply as written, without user edits.
- Invoking `auto` is the user's assertion that no other session is using the store.
- Flagged entries have no one to decide them, so every flagged entry is kept. Still list them in `review.md` under "Needs user decision" for later human review.
- Every artifact is still created along the way: the verified backup, `export.txt`, `review.md`, and `import.txt`. At the end, report the complete path of each one so the user can audit the run afterwards.

## Steps

0. **Confirm exclusive access** — Parallel sessions may share the store. Ask the user to confirm that no other session using this memory store is running. Do not touch the store until they confirm; if they cannot confirm, stop.
   Done when: the user has confirmed that no other session is active.

1. **Prepare** — Run `memo wake` (or the store's memory instructions) and finish every pending compression: repeat `memo nap` until it prints `Nothing left to compress.` The tree must be complete before export, or summaries will be missing.
   Done when: `wake` prints `You are awake.` and `nap` prints `Nothing left to compress.`

2. **Locate the store** — Find the memory directory (`$MEMORY_DIR`, or `~/.optmem/memory`) and the `memo` tool (`which memo`, or a vendored copy such as `.optmem/memo`). Run `memo config` to confirm the store is reachable.
   Done when: both paths are known and `memo config` prints the store's sizes.

3. **Back up** — Create `optmem-clean-YYYYMMDD/` (today's date) in the working directory.
   - Git-tracked store: explicitly add only the memory store paths and commit them with `chore(optmem): backup memory before clean`. Verify the commit's `LOG.txt` has the same byte size as the working tree, and that `git status --porcelain -- <memory store paths>` prints nothing (so `LOG.txt` and every `TREE/` file are all committed).
   - Otherwise: copy the whole memory directory (`LOG.txt`, `TREE/`, `config`) into `optmem-clean-YYYYMMDD/backup/` and verify byte sizes match.
   Done when: the backup is verified before anything else changes.

4. **Export everything** — Run:
   `scripts/optmem_cleaner.py export --memory-dir <memory dir> -o optmem-clean-YYYYMMDD/export.txt`
   It dumps every raw memory and every tree summary.
   Done when: the printed raw and summary counts match the store's contents.

5. **Show the criteria** — Present the Cleaning criteria to the user (they are short, and the user may edit them) and state the complete path of the export file. Do not paste the export into the reply. Ask whether they want to edit the criteria; do not curate until they confirm (or edit).
   Done when: the user has approved or edited the criteria.

6. **Curate** — Write `review.md` in the archive folder containing: (a) the full export, (b) the proposed cleaned list (each entry: keep / merge / delete / flag, reason, source ids), (c) the criteria, (d) a "Needs user decision" section listing every flagged entry. Apply the criteria by hand; resolve old-id references by hand.
   Done when: every exported memory is accounted for (kept, merged, deleted, or flagged with a reason) and the proposed list has no duplicates or gaps.

7. **User review** — Tell the user the complete path of `review.md` and wait. Do not paste its contents into the reply. The user may edit it or reply with changes; they also decide every entry in the "Needs user decision" section. Incorporate their edits and decisions into the proposed list.
   Done when: the user explicitly approves the reviewed list.

8. **Prepare the import file** — From the approved list, write `import.txt` in the archive folder: one `YYYY-MM-DD <text>` line per entry, chronological, each within the store's entry size limit (`ENTRY_CHARS` from the `config` file inside the memory directory, 280 bytes when absent). Then run:
   `scripts/optmem_cleaner.py check import.txt --memory-dir <memory dir>`
   Done when: check exits 0.

9. **Diff and second confirmation** — Show the user: old count → new count, the deleted and merged entries, and the exact paths that will be cleared. If the proposed list is identical to the current store, stop here — there is nothing to clean. Then ask explicitly: "Clear the store and import the new list?" Do not proceed without a clear yes.
   Done when: the user has confirmed.

10. **Clear** — Inside the memory directory: empty `LOG.txt` (0 bytes) and delete every file in `TREE/`. Touch nothing else.
    Done when: `LOG.txt` is 0 bytes and `TREE/` contains no files.

11. **Import** — Run `memo import optmem-clean-YYYYMMDD/import.txt` (or the tool's full path). It validates the entire file before writing and appends atomically, preserving each entry's date.
    Done when: the tool prints `Imported N memories`.

12. **Compress** — Repeat `memo nap` until it prints `Nothing left to compress.` Each block's summary is written by you, not by the tool: write it by the Cleaning criteria, keeping only durable facts. Finish every compression in this session; do not leave pending compressions behind.
    Done when: `nap` reports nothing left.

13. **Verify** — Run `memo wake` once and read to the end of its output. Confirm the new entries appear and `You are awake.` is printed.
    Done when: wake succeeds and shows the new store.

14. **Finish** — Report old count → new count, the date range, the archive folder, and the backup location. Frame the counts as a quality outcome, not a slimming achievement. If a large share of the store was deleted, say so plainly: it means too much noise was being recorded upstream, and the note-taking discipline that produced it needs fixing. If the memory directory is git-tracked, add the memory store paths explicitly and commit `chore(optmem): clean memory`, then follow the repository's push convention if one exists.
    Done when: the report is delivered and the optional commit is made.

## Failure recovery

If clearing or importing goes wrong, restore from the verified backup, then compress and verify again:

- Git-tracked store: `git checkout <backup commit> -- <memory store paths>`.
- Copied store: copy the files from `optmem-clean-YYYYMMDD/backup/` back into the memory directory.

After restoring, repeat `memo nap` until nothing is left, then `memo wake` once.

See `REFERENCE.md` for store formats, size limits, and tool behaviour.
