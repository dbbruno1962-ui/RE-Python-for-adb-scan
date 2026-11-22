# Operator investigation rules

## Evidence-first procedure

Before designing or changing a mechanism, inspect applicable Hypertext records, then the relevant source, configuration, examples, reports, and logs. Reuse an existing validated path when it answers the same question with less invasive changes. Record why a path was reused or rejected and the evidence for that choice.

## Exhaust relevant evidence

Do not stop at the first plausible supporting result. Inspect relevant definitions, implementations, callers, wrappers, configuration, scripts, and observed behavior. Search for contradictory evidence. For comparisons, examine equivalent layers and states and identify gaps rather than treating missing analysis as a difference.

## Experiments

State the unknown or competing hypotheses, the observations that distinguish them, and whether existing or read-only evidence can answer the question first. Preserve validated state, vary only relevant factors, and choose the least invasive experiment with useful discriminatory power. Reversibility protects state; it is not evidence.

## Causality and completion

Trace trigger, decision, state transition, action, side effects, and observable result before attributing causality. Prefer falsifiable explanations and retain unresolved alternatives. Report scope, contradictory evidence searched, residual unknowns, and work still planned. A semantic gap in the relevant causal path blocks an equivalence claim until its effect is bounded.

For any state-changing action, preserve concise chronological details: timestamp if known, actor/target, tool or artifact actually used, parameters, expected effect, observed result, and resulting state. Do not invent unobserved intermediate transitions.
