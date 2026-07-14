# lob-continuity

A validity framework for detecting silent continuity gaps in limit order
book reconstruction.

## Why this exists

Depth-update streams (e.g. exchange WebSocket feeds) can silently drop
messages. A naively reconstructed order book keeps looking valid after a
drop — it just becomes wrong. `lob-continuity` detects breaks in
sequence-ID continuity and marks the resulting segments, rather than
interpolating across them. See [docs/why_validity_matters.md](docs/why_validity_matters.md)
for the full argument.

## Architecture

\`\`\`mermaid
flowchart LR
    A[Depth update stream] --> B[detect_continuity]
    B --> C[ContinuitySegment list]
    B --> D[Gap intervals]
\`\`\`

## Quickstart

\`\`\`bash
pip install -e ".[dev]"
python examples/demo.py
\`\`\`

## Status

Early-stage / actively developed.

## License

MIT — see [LICENSE](LICENSE).