# CLAUDE.md

Guidance for Claude Code (claude.ai/code) when it works in this repository.

## Context

`lob-continuity` is the open-source data-validity layer of my PhD research on
limit-order-book microstructure at University College Dublin. The research
pipeline reconstructs order books from exchange depth-update streams. Every
downstream result depends on knowing which intervals of that reconstruction
can be trusted, and that question is what this library answers.

I write and own this code. Claude Code is my coding assistant: it drafts and
reviews code, writes tests and challenges design decisions. I review every
change before it is committed.

## Scope (read first)

This repository is public. It covers **data trustworthiness** for
reconstructed limit order books: is a given interval clean, how do we know,
and what happens when it is not.

In scope:

- sequence-gap detection (`detector.py`)
- the synthetic depth-update simulator (`simulator.py`) that exercises it

Out of scope, and kept in the private research codebase:

- modelling, forecasting, feature engineering, or any interpretation of what
  clean data implies. This library stops at "the interval is valid or
  gap-bounded".
- captured market data, venue-specific calibration, symbol lists or parameter
  values. The simulator ships synthetic fixtures only.
- infrastructure, host, provider or credential details.

Widening this scope is my decision. If a task looks like it crosses this
line, stop and ask.

## How to work here

- **Plan before code.** For anything non-trivial, propose the approach and the
  trade-offs before writing it.
- **Explain non-obvious choices.** Typing decisions, standard-library options,
  failure modes and edge cases belong in the review discussion, and in
  docstrings where a future reader needs them.
- **Small, reviewable diffs.** Prefer a focused change with tests over a large
  rewrite.
- **Fail closed.** Malformed, overlapping or out-of-order input raises
  `ValueError`. Never guess, repair or interpolate silently.

## Git is owner-only

Only I run `git commit` and `git push`. Claude Code edits working files, runs
lint, type checks and tests, and stops there. It may suggest a commit message.
This keeps a human review on every change to a public repository.

## Design

Depth-update streams can silently drop messages. A naively reconstructed book
stays structurally valid after a drop but becomes wrong. The library detects
breaks in **update-ID continuity**, not wall-clock continuity, and partitions
the stream into segments, marking gaps rather than interpolating across them.
See `docs/why_validity_matters.md` and
`docs/resampling_requires_valid_segments.md`.

Data flow: ordered depth-update stream → `detect_continuity` →
`ContinuityReport` (continuous segments plus the explicit gaps between them).

## Commands

```bash
pip install -e ".[dev]"   # package + dev tools (pytest, ruff, mypy)

ruff check .              # lint
mypy src/                 # type-check (strict)
pytest                    # tests
pytest tests/test_detector.py::test_name   # a single test
```

CI (`.github/workflows/ci.yml`) runs `ruff check .`, `mypy src/` and `pytest`
on Python 3.11. All three must pass locally before a push.

## Conventions

- `mypy` runs in strict mode; all code is fully typed.
- Python >= 3.11; line length 100 (ruff).
- Domain rule: continuity is defined by the update-ID sequence, never by
  timestamps. A wall-clock pause is not a break; a sequence jump is. Never
  interpolate across a detected gap. Mark it.
