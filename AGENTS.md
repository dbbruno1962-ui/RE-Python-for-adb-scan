# REConsole project rules

## Evidence before conclusions

- Treat acquired logs, reproduced behavior, checked-in source, and configuration as evidence; keep them distinct from inference and hypothesis.
- Label claims **Observed**, **Derived**, **Inferred**, **Hypothesis**, or **Unknown** where the distinction matters. Do not promote a hypothesis into a fact in reports, `reports/status.md`, plans, or later sessions.
- Do not reopen a decision settled by evidence unless new evidence bears on it.
- Prefer an existing, validated, less invasive path. Preserve knowledge from unsuccessful or rejected paths.
- Keep real device logs and secrets out of version control. Use sanitized or synthetic examples where possible.

## Status is project memory

`reports/status.md` is an append-only session journal. It records verified findings, provisional interpretations, open questions, constraints, decisions, actions, and next steps. Writing down unfinished work does not make it complete.

Append new dated entries; do not rewrite, reorder, or consolidate historical entries. Correct an earlier statement with a new entry that identifies it and explains the evidence for the correction. Each relevant session entry should distinguish findings from open investigation and planned work. Record state-changing actions in observed order, including target, tool or script, relevant parameters, expected effect, result, and resulting state when known. Mark unknown transitions as unknown.

Before appending, inspect the existing journal and preserve its history. `REConsole/reports/status.md` is the canonical local journal; `REConsole/reports/mirror/status.md` is its byte-identical verification mirror and append checkpoint. First verify they match. After appending only to the canonical journal, verify that the old mirror is an exact byte prefix of the new journal; only then refresh the mirror and verify equality and SHA-256. This detects edits, deletions, reordering, or insertion within previously journaled history. Stop on mismatch; do not repair divergence silently. Do not use the sibling worktree's Yi/Anyka status paths.

## Hypertext semantic records

`hypertext/` is the structured semantic index for REConsole knowledge. It complements rather than replaces source files, logs, reports, and `reports/status.md`. Maintain provenance links and explicit epistemic, lifecycle, applicability, and coverage states. Preserve conflicts until authoritative evidence resolves them. Do not copy sibling-worktree device records as if they applied here.

Start retrieval from `hypertext/index.md` for an area already represented there, then follow its records to primary evidence and relevant status history. Read `reports/status.md` directly when Hypertext lacks coverage, has a conflict or gap, or chronology/provenance is requested.

## Investigation and experiments

Before changing a mechanism, inspect the applicable Hypertext entries, source, configuration, examples, and prior logs or reports. Search for evidence that could contradict the leading explanation. Trace causal behavior through trigger, decision, state transition, action, side effects, and observable result where relevant.

Choose experiments for their ability to distinguish hypotheses. Prefer read-only observations when they answer the question. Preserve validated state and avoid unrelated changes. Report unresolved gaps and do not describe planned work as completed.

## Role-document routing

These role documents are mandatory continuations for their triggers:

| Document | Trigger |
|---|---|
| `.agent-rules/operator/investigation.md` | Design, analysis, evidence review, experiment, or causal investigation |
| `.agent-rules/operator/hypertext-retrieval.md` | Hypertext retrieval during investigation |
| `.agent-rules/curator/hypertext.md` | Creating, assimilating, validating, or reconciling Hypertext records |
| `.agent-rules/curator/status.md` | Appending status, handoff, or checking historical integrity |

Read every triggered document before the applicable action. A missing or unverifiable document means stop that action and report the gap.

## Deployable artifacts

Do not replace or promote a deployable artifact as tested/current without durable identity and provenance. Record intentionally unexecuted changes as **NOT RUN**. A source edit, successful packaging, or configuration update alone does not establish runtime behavior.

## Scope boundary

REConsole is the Python/PySide6 ADB log acquisition and correlation application, with Wi-Fi snapshots and local filtering. Reverse-engineering material under `vidure_re_output/` concerns a separate ZHENYI/SGK telescope camera and must not be treated as REConsole runtime evidence. The Yi camera capture script is a separate acquisition workflow. Keep claims and evidence scoped to their actual target.
