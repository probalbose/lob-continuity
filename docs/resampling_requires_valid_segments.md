# Resampling requires valid continuity segments

A faster update stream can be represented on a slower regular clock only after
the supplied update spans have been checked for continuity.

Suppose one valid segment contains update spans 100 through 104, followed by
105 through 108. A downstream process may sample states from that segment at a
declared interval because every supplied span between its boundaries is
accounted for.

If the next observed span instead starts at 112, update IDs 109 through 111 are
not present. Sampling across that boundary would make a regular-looking path
through evidence that was never observed. A slower clock does not repair the
gap. It only makes the gap easier to overlook.

The safe order is therefore:

```text
ordered update spans
        |
        v
continuity detection
        |
        +--> valid segment --> declared resampling may proceed
        |
        +--> explicit gap --> stop; do not interpolate across it
```

This repository supplies the continuity decision and explicit boundaries. It
does not implement downstream resampling or interpret what a sampled path
means.
