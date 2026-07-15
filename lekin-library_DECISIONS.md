# Decisions Log — lekin-library

Append-only log of changes made to `lekin-library`, in order, with reasoning.
Read this whole file at the start of every new session before doing any work.
Never delete or rewrite past entries — if a decision is later reversed, add a
new entry saying so and why, rather than editing the old one.

Each entry should follow this format:

```
## [YYYY-MM-DD] <short title>
- Branch: <branch name>
- Item: <which Phase 0 item this corresponds to, if applicable>
- What changed:
- Why:
- Alternatives considered / tradeoffs:
- Tests added:
- Status: (in review / merged / reverted)
```

---

## [YYYY-MM-DD] Project baseline
- Branch: n/a
- Item: n/a
- What changed: Cloned `Lekin_Python` from
  https://github.com/mpinedo170/Lekin_Python as the starting point for
  `lekin-library`. No code changes yet.
- Why: Establishing the baseline before Phase 0 refactor work begins.
- Alternatives considered / tradeoffs: n/a
- Tests added: none (pre-existing `tests/test_io_integers.py` carried over as-is)
- Status: merged

<!-- Add new entries below this line, most recent last. -->

## [2026-07-15] Item 1: Operation-level schedule model
- Branch: refactor/scheduling-engine-phase0
- Item: Phase 0, item 1 of 7 (see task list below)
- What changed:
  - Added `ScheduledOperation` (`lekinpy/schedule.py`): job_id, operation_index,
    workcenter, machine, start_time, end_time, sequence_position, status, with
    `to_dict`/`from_dict`.
  - `MachineSchedule.operations` changed from `List[str]` (job ids) to
    `List[ScheduledOperation]`; `to_dict`/`from_dict` updated to match.
  - `Schedule` gained an optional `rgb` field (default `None`) so `.seq`'s RGB
    line round-trips instead of crashing (see bug found, below).
  - `base.py::_assign_single_operation` now builds and stores a
    `ScheduledOperation` per assignment instead of appending a bare job-id
    string. This is the only algorithm-side touch in this item — the actual
    multi-operation scheduling bug (SPT/EDD/WSPT only ever scheduling
    `operations[0]`) is untouched here; that's item 2.
  - `io.py`: `.seq` export now writes full operation data per line
    (`job_id;operation_index;start_time;end_time;sequence_position;status`);
    `parse_seq_file` reads that back, while still tolerating original bare
    job-id LEKIN `.seq` files (real examples confirmed under `Data/Job Shop/`)
    by leaving timing fields `None` for those. Added `load_schedule_from_json`
    for symmetry with `save_schedule_to_json`.
  - `display_machine_details`, `display_job_details`, `plot_gantt_chart`,
    `display_sequence` patched only enough to not crash on the new type
    (read `so.job_id` instead of treating the list item as the id directly).
    They still recompute timing from `job.operations[0]` rather than reading
    the stored `ScheduledOperation` timing — that recompute-vs-stored-data
    fix is deliberately deferred to item 3.
- Why: `MachineSchedule` stored only job IDs, so every reporting/plotting
  method had to re-derive timing from `job.operations[0]` on the fly, which
  is both wasteful (the real timing already exists on the `Operation` object
  after scheduling) and wrong for multi-operation jobs (always uses the first
  operation's duration no matter which operation actually ran on that
  machine). Storing the full placement record is the prerequisite for both
  the item 2 fix (multi-op algorithms) and the item 3 fix (reporting reads
  real data).
- Bugs found while inspecting (pre-existing, not introduced by us):
  - `save_schedule_to_seq` referenced `schedule.rgb`, which `Schedule` never
    defined as an attribute — would raise `AttributeError` on any real call.
    Fixed by adding the optional `rgb` field.
  - `Schedule.from_dict` didn't handle the `rgb` key that `parse_seq_file`
    produces, and used `MachineSchedule(**m)` directly, which broke once
    `MachineSchedule.operations` held objects instead of plain strings.
- Alternatives considered / tradeoffs:
  - Considered keeping `MachineSchedule.operations` as job-id strings and
    adding a parallel `timings` dict — rejected because it re-creates the
    exact "derived data can drift from source" problem we're trying to
    remove, and doesn't support a job visiting the same machine more than
    once (job_id alone would be ambiguous without operation_index).
  - Considered making `ScheduledOperation.status` a scheduling-state enum
    ("scheduled"/"in-progress"/"done") instead of copying `Operation.status`.
    Went with copying the source `Operation.status` verbatim since that's the
    only status concept the codebase currently has, and inventing a new one
    wasn't asked for.
- Tests added: `tests/test_schedule_model.py` — `MachineSchedule` holds
  `ScheduledOperation` objects, multi-op precedence timing is correct,
  lossless JSON round-trip, lossless `.seq` round-trip, and legacy bare
  job-id `.seq` files parse without crashing.
- Status: in review (not yet merged to master; full suite passes: 7/7)

## Observed, not yet actioned
<!-- Anything noticed while working that's out of scope for the current
     item — note it here instead of fixing it inline, so it isn't lost. -->
- `examples/fcfs_example.py` still treats `MachineSchedule.operations` as a
  list of job-id strings (e.g. `for job_id in ms.operations`) and will break
  if run as-is after item 1. It's outside the packaged library (excluded
  from `setuptools.packages.find`) and isn't a test, so left alone for now.
  Fix in a final example-scripts cleanup pass, or earlier if asked.
- `docs/API_REFERENCE.md` documents the old `MachineSchedule(operations:
  list[str])` shape and explicitly calls out the single-operation assumption
  for SPT/EDD/WSPT — needs a pass once items 1-3 are all done, so it isn't
  half-updated mid-refactor.

## Task list (Phase 0 — refactor lekin-library, per user request 2026-07-15)
1. Operation-level schedule model — done, see entry above (in review)
2. Fix multi-operation scheduling in SPT/EDD/WSPT — not started
3. Rewrite Gantt/reporting to read from real ScheduledOperation data — not started
4. Validation layer (typed exceptions) — not started
5. Formalize SchedulingAlgorithm plugin contract (metadata dict) — not started
6. Backward compatibility check for System/Job/Operation/Machine/Workcenter constructors — ongoing constraint, not a discrete step
7. Tests for every change above — being added alongside each item, not deferred to the end
