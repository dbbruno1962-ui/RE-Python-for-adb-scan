# Curator status rules

`reports/status.md` is an append-only project journal. Append new dated entries only; do not retroactively correct, delete, reorder, or consolidate history. Correct or supersede prior statements in a new entry that identifies the earlier statement and gives the evidence or reason.

`reports/mirror/status.md` is the byte-identical verification mirror and append checkpoint. The canonical journal is the only append target. Before appending, verify that journal and mirror are byte-identical. After appending, verify that the old mirror is an exact byte prefix of the new canonical journal (compare exactly the old mirror's byte length); only then copy the canonical journal to the mirror, confirm byte identity with `cmp`, and compare SHA-256 values. This detects edits, deletions, reordering, and insertion within previously journaled history. Do not edit the mirror independently. Record verification failure and stop; never silently repair unexpected divergence.

At a handoff or append, include the concise causal action history needed to reconstruct relevant state changes. Separate verified findings, provisional interpretations, open questions, constraints, and planned work. A documented open question remains open.

The mirror checkpoint is initialized for this worktree and is the baseline for detecting non-append changes on subsequent journal updates. It is not an imported checkpoint from an earlier journal. If a separate Hypertext assimilation checkpoint is introduced, preserve an immutable witness and verify the prefix before assimilation; any unexplained mismatch requires human review rather than automatic repair.
