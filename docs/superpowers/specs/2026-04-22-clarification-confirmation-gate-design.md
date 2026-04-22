# Clarification Confirmation Gate Design

## Goal

Expose the planner's clarification questions and default assumptions in the run detail UI, then let the user either:

- accept the current default assumptions and continue execution immediately, or
- reject the current default assumptions, submit corrective feedback, and force the planner to regenerate the plan or return a new clarification gate.

This applies to runs in `WAITING_CLARIFICATION` only.

## Current State

- The backend already pauses execution when PC marks the requirement ambiguous.
- The checkpoint already stores the useful clarification context inside `serialized_state.node_outputs.PC`.
- The frontend currently knows only that a clarification is pending. It does not know the actual questions, assumptions, or planning summary.
- The existing `POST /api/runs/{run_id}/clarify` endpoint always expects free-form clarification text and cannot distinguish "accept defaults" from "reject defaults".

## Desired UX

Inside the existing run detail page:

1. When `pendingAction.action_type === "clarification"`, show a `Clarification Gate` panel above the workflow graph and timeline.
2. The panel presents:
   - the planner's current requirement brief
   - the planner's default assumptions
   - the planner's explicit clarification questions
   - a compact plan draft summary so the user can judge what will happen next
   - the most recent clarification history entries, when present
3. The user gets two distinct actions:
   - `Confirm Current Defaults and Continue`
   - `Reject Current Defaults`
4. `Confirm Current Defaults and Continue` opens a confirmation-only dialog with no text input.
5. `Reject Current Defaults` opens a dialog with a required textarea for corrective feedback.
6. After submission:
   - confirm path resumes execution immediately
   - reject path resumes execution with the new user feedback added to state and memory
7. If PC still finds ambiguity after the reject path, the run returns to `WAITING_CLARIFICATION` with a new brief, new assumptions, and possibly new questions.

## Recommended API Shape

Keep the existing endpoint surface small by extending `pending-action` and `clarify`.

### Read API

Extend `GET /api/runs/{run_id}/pending-action` to include a clarification payload when `action_type === "clarification"`.

Add a nested object:

```json
{
  "clarification_context": {
    "requirement_brief": "Build a sakura landing page...",
    "clarifying_questions": ["What is the page goal?"],
    "assumed_defaults": ["Static single-page site"],
    "acceptance_criteria": {
      "must_have": ["hero", "cta"],
      "should_have": ["responsive layout"],
      "could_have": ["light animation"]
    },
    "work_breakdown": ["clarify scope", "implement page"],
    "clarification_history": [
      {
        "message": "Use Chinese copy and no form.",
        "target_role": "PC"
      }
    ]
  }
}
```

### Write API

Extend `POST /api/runs/{run_id}/clarify` request body from:

```json
{
  "message": "..."
}
```

to:

```json
{
  "decision": "accept_defaults",
  "message": "",
  "structured_context": {}
}
```

or:

```json
{
  "decision": "reject_defaults",
  "message": "The page is for an event landing page in Chinese, use a fresh Japanese tone, no form, mobile responsive.",
  "structured_context": {
    "preferences": {
      "language": "zh-CN",
      "responsive": true
    }
  }
}
```

## Decision Semantics

### Accept Defaults

- The frontend sends `decision = "accept_defaults"`.
- No free-form input is shown.
- Backend accepts an empty `message`.
- Backend writes a clarification record with a generated system message such as:
  `User accepted the current default assumptions and requested execution to continue.`
- Backend clears the clarification gate and resumes the run using the existing restart path.

### Reject Defaults

- The frontend sends `decision = "reject_defaults"`.
- `message` is required and must be non-empty.
- Backend persists the user feedback as both clarification history and memory.
- Backend clears PC and downstream node outputs using the existing clarification-reset logic.
- Backend restarts the run from the planner so PC can regenerate the requirement brief, plan draft, and new clarification questions if needed.

## Backend Design

### Schema Changes

Add a clarification decision enum-like field to the clarification request schema, plus a new nested response model for clarification context.

Suggested additions:

- `ClarificationDecision = Literal["accept_defaults", "reject_defaults"]`
- `ClarificationContextRead`
- extend `PendingActionRead` with `clarification_context: ClarificationContextRead | None`

### Route Behavior

`GET /runs/{run_id}/pending-action`

- Read the latest checkpoint state.
- If the run is waiting for clarification, extract data from `state["node_outputs"]["PC"]`.
- Normalize missing values to empty strings, empty arrays, or empty objects.
- Include recent `clarification_history` from checkpoint state.

`POST /runs/{run_id}/clarify`

- Branch on `payload.decision`.
- If `accept_defaults`, allow blank `message` and synthesize a stored message.
- If `reject_defaults`, validate non-empty `message`.
- Keep the current checkpoint-resume mechanism and node reset behavior.
- Preserve existing preference upsert behavior from `structured_context.preferences`.

### State Source of Truth

Keep the checkpoint as the transient source of truth for clarification context. Do not duplicate this into the `runs` table.

Rationale:

- the context is already generated by PC and checkpointed
- it changes per cycle and per clarification round
- it is not stable run metadata

## Frontend Design

### New UI Component

Add a dedicated run-detail component, for example `ClarificationGatePanel`, with these responsibilities:

- render clarification context from `pendingAction`
- render the two action buttons
- manage dialog open and close state
- submit clarification decisions
- show request error state and submitting state

### Panel Content

The panel should display:

- `Current Understanding`
  - planner-generated `requirement_brief`
- `Default Assumptions`
  - ordered bullet list from `assumed_defaults`
- `Questions to Resolve`
  - ordered bullet list from `clarifying_questions`
- `Plan Draft`
  - compact rendering of `acceptance_criteria` and `work_breakdown`
- `Recent Feedback`
  - latest clarification history items, newest first or truncated to the most recent 3 entries

### Dialogs

#### Confirm Dialog

- Title: `Continue with current default assumptions?`
- Body explains that the system will resume planning and implementation using the displayed assumptions.
- Actions:
  - `Continue Execution`
  - `Cancel`
- No textarea.

#### Reject Dialog

- Title: `Reject current default assumptions`
- Required textarea.
- Help text explains that the user should describe what is wrong and what should change.
- Actions:
  - `Submit Feedback`
  - `Cancel`

### Refresh Strategy

After either action succeeds:

- refresh run detail
- refresh pending action
- refresh graph if present

Expected results:

- run becomes `RUNNING` if execution resumes normally
- run returns to `WAITING_CLARIFICATION` with a new clarification payload if PC still lacks enough information

## Error Handling

### Backend

- `409` if the run is no longer in `WAITING_CLARIFICATION`
- `422` or `400` if `reject_defaults` is submitted with an empty message
- tolerate missing PC output in `pending-action` by returning an empty clarification context rather than crashing

### Frontend

- If submit returns `409`, show a non-blocking message and immediately reload the run state
- Disable submit buttons while requests are in flight
- Keep the reject textarea contents on failed submission

## Testing Strategy

### Backend Tests

Add route-level tests to verify:

- `pending-action` returns clarification context extracted from checkpoint state
- `accept_defaults` with empty message succeeds and resumes execution
- `reject_defaults` with empty message fails validation
- `reject_defaults` with non-empty message records feedback and resumes from PC
- if PC re-enters clarification, the new context is visible through `pending-action`

### Frontend Tests

If a frontend test runner is added or already exists later, cover:

- clarification panel renders requirement brief, assumptions, and questions
- confirm flow opens a dialog with no input
- reject flow opens a dialog with required input
- success path reloads page state
- error path preserves user input and surfaces the error

For the current repo state, the minimum verification remains `next build` plus manual run-through against a real waiting-clarification run.

## File Impact

Expected backend files:

- `apps/api/app/models/schemas.py`
- `apps/api/app/api/routes.py`
- optionally `apps/api/app/api/serializers.py` if normalization helpers are extracted
- `apps/api/tests/test_execution_runtime_graph.py` or a new API-focused test file

Expected frontend files:

- `apps/web/app/runs/[runId]/page.js`
- new component such as `apps/web/app/components/ClarificationGatePanel.js`
- optional shared dialog styling in `apps/web/app/globals.css`

## Non-Goals

- per-question answer capture
- a separate clarification inbox page
- changing approval flow behavior
- redesigning the run detail layout outside the clarification panel and dialogs

## Open Decisions Resolved

- Accept path is confirmation-only and contains no input field.
- Reject path requires user feedback.
- Reject path must trigger replanning, not passive storage.
- The replanning result may be a new plan draft or another clarification gate, depending on what PC determines after seeing the user's feedback.
