A tweaked version of [the original AGENTS.md prompt](https://github.com/VictorTaelin/OptMem#the-prompt) with more constraints for agents when register memories.

```

## Memory

Your memory is OptMem (lives inside this repo at `.optmem/`):
- The tool is `.optmem/memo` (run from the repo root)
- Your memories are in `.optmem/memory`
- The tool defaults to `~/.optmem/memory`, so every invocation must set `MEMORY_DIR`, e.g. `MEMORY_DIR="$PWD/.optmem/memory" ./.optmem/memo wake`

OptMem outlives every session, compaction, model and vendor change.
Without it you do not know who you are, or what was decided and tried.

### At startup: activating OptMem (mandatory)

Run `MEMORY_DIR="$PWD/.optmem/memory" ./.optmem/memo wake` before any other tool call, in every session, and then read through exactly what it prints, to the end of its output, these are the memories you accumulated from the past sessions.

### While working: register memories (mandatory)

Call `MEMORY_DIR="$PWD/.optmem/memory" ./.optmem/memo note "<1 line, max 280 bytes>"` whenever you learn something new, or something worth keeping happens. 

That covers a task worth real effort, a fact or insight the user teaches you, anything you learn about their life (even indirectly), any event of lasting effect. 

A memory note should always be durable: still useful to a future session, possibly on an unrelated task. If a note is useful only until the current task ends -> do not record.

Never record:
- Work logs: tasks finished, rounds completed, commits, pushes, validations run. Git history already holds all of this.
- Transient state: current progress, next steps, which files you staged.
- Per-task only operational rules that won't be useful for future sessions.

When in doubt, do not record. A few dense memories beat a noisy log.

Do not register redundant memories.

When you found an existing memory is outdated, register a new memory note about this.

If `memo note` asks a compression: do it before your next action.

Never edit or delete anything under `.optmem/memory`: the tool manages it.

### When you need an old memory: search, or navigate

`MEMORY_DIR="$PWD/.optmem/memory" ./.optmem/memo recall <regex>` searches every memory, word for word.

Your memories also form a binary tree: #0-1, #2-3 ... exist as one-line summaries, pairs of those as #0-3, and so on -- every `#a-b` line wake prints is one node of it. `MEMORY_DIR="$PWD/.optmem/memory" ./.optmem/memo zoom <a-b>` opens a node into its two halves, down to the raw memories.

### If you're a subagent: skip everything above

Parallel sessions on this machine are all you, and may all write memories.

A subagent is not: it must never run `memo`, because it cannot judge what is already known, and its notes would arrive duplicated and incorrectly.

When you spawn one, write: `You are a subagent. Don't run memo.`

```