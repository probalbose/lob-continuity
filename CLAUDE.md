# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Public disclosure boundary (read first)

This repository is **public**. It exists to demonstrate one thing: **data
trustworthiness** for reconstructed limit order books — is a given interval
clean, how do we know, and what happens when it is not.

Scope is deliberately narrow. In-scope work is limited to:

- **sequence-gap detection** (`detector.py`), and
- a **synthetic depth-update simulator** (`simulator.py`) used to exercise it.

Do **not** add, and do not let a request pull in:

- modelling, forecasting, feature engineering, or any interpretation of what
  clean data *implies* — this repo stops at "the interval is marked valid or
  gap-bounded"; it never reasons about what the data means;
- real captured market data, exchange-specific calibrations, symbol lists, or
  parameter values — the simulator ships synthetic fixtures only;
- infrastructure, host, provider, or credential details — if infra is
  mentioned at all, keep it generic (e.g. "a small dedicated Linux box").

Widening this scope (new modules, real-data artefacts) is an owner decision made
outside this repo — not something to infer from a coding request. If a task
seems to cross this line, stop and ask. A local, uncommitted checklist and a
pre-commit sweep enforce the finer-grained rules; see `.boundary/boundary-local.md`
if present.

## How we work here (pair programming, not autopilot)

This repo is developed as a **pair**: Probal (the owner) and Claude Code writing
code together. The point is not just to ship the library — it is for Probal to
learn Python (and good library-design habits) while building it. Work in that
spirit:

- **Teach while doing.** When you write code, explain the *why* — idioms,
  typing choices, standard-library options, trade-offs, and any Python-specific
  gotchas. Prefer a short explanation over a silent large diff. Treat every
  change as a chance to explain the language.
- **Leave room for the owner to write code too.** Don't implement an entire
  feature end-to-end by default. Offer to split the work — e.g. you scaffold and
  do one part, Probal writes the next — and when useful, outline the approach
  and let Probal attempt it first, then review and refine together.
- **Default to plan-then-do.** For anything non-trivial, propose the approach
  and discuss it before writing code, so it's a conversation, not a handoff.
- **Review Probal's code constructively.** Point out bugs, typing issues, and
  cleaner alternatives, and explain the reasoning so the lesson sticks.

## Git is owner-only

**Probal is the only one who runs `git commit` and `git push`. Claude Code must
never commit, push, or otherwise write to git history — not even when asked in
passing.** Claude may stage nothing on its own; it edits working files, runs
tests/lint/type-checks, and stops there. Prepare changes and *suggest* a commit
message if helpful, but the owner reviews the diff and makes every commit. This
keeps the disclosure boundary (above) under a human check on every commit.

## What this is

A validity framework for detecting silent continuity gaps in limit order book (LOB)
reconstruction. Depth-update streams (e.g. exchange WebSocket feeds) can silently drop
messages; a naively reconstructed book stays *structurally* valid after a drop but becomes
*wrong*. This library detects breaks in **sequence-ID (update-ID) continuity** — not
wall-clock continuity — and partitions the stream into segments, marking gaps rather than
interpolating across them. See `docs/why_validity_matters.md` for the motivating argument.

## Project state

Early-stage scaffold. The public API is stubbed and not yet implemented:

- `src/lob_continuity/detector.py` — `detect_continuity()`, `ContinuitySegment`,
  `ContinuityReport`. Dataclass fields and the detection logic are `TODO(owner)`;
  `detect_continuity` currently raises `NotImplementedError`.
- `src/lob_continuity/simulator.py`, `src/lob_continuity/__init__.py` — empty.
- `tests/test_detector.py`, `examples/demo.py` — empty (README references `demo.py` as the
  quickstart, so it is expected to be fleshed out).

When implementing, the intended data flow is: ordered depth-update stream →
`detect_continuity` → a `ContinuityReport` holding a list of `ContinuitySegment`s plus the
gap intervals between them.

## Commands

```bash
pip install -e ".[dev]"   # install package + dev tools (pytest, ruff, mypy)

ruff check .              # lint
mypy src/                 # type-check (strict mode)
pytest                   # run tests
pytest tests/test_detector.py::test_name   # run a single test
```

CI (`.github/workflows/ci.yml`) runs `ruff check .`, `mypy src/`, then `pytest` on Python
3.11. Match all three locally before pushing.

## Conventions

- `mypy` runs in **strict** mode — all new code must be fully typed.
- Requires Python >=3.11; line length 100 (ruff).
- Domain rule to preserve: continuity is defined by update-ID sequence, *not* timestamps.
  Do not treat wall-clock gaps as continuity breaks, and never interpolate across a
  detected sequence gap — mark it.
