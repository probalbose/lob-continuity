# Why continuity validity matters

A reconstructed limit order book may look plausible after an update has been
missed. Prices can remain ordered, quantities can remain positive, and the
program can continue without an exception. Nevertheless, every later state may
have been computed from incomplete evidence.

## Sequence IDs, not elapsed time

Wall-clock timing cannot prove continuity. Two valid events may be separated
by a quiet period, while two events arriving close together may still have an
unobserved sequence span between them. The continuity decision therefore uses
the update IDs carried by adjacent events.

Suppose one event covers update IDs 100 through 104 and the next starts at
105. Those spans are continuous. If the next starts at 109, update IDs 105
through 108 were not observed. The detector closes the current valid segment,
records the four-ID gap, and starts a new segment at 109.

The four missing IDs do not necessarily mean four network messages were lost.
A single message may cover several update IDs. The library reports what the
identifiers establish and does not infer an unobserved message count.

## Mark the boundary instead of inventing data

Interpolating across a sequence gap would create a smooth-looking book without
source evidence. This library instead returns maximal continuous segments and
the explicit gaps between them. A downstream reader can then accept a segment
or decline an interval by construction.

## What this library does not claim

The detector assumes its input is already ordered and de-duplicated. It rejects
malformed, overlapping, or out-of-order spans because resolving those cases
requires a separately declared source contract. It also makes no claim about
market behaviour. Its result is narrower and auditable: which supplied spans
were continuous, where continuity broke, and how many update IDs were absent.
