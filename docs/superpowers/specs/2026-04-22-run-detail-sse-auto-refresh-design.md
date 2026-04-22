# Run Detail SSE Auto-Refresh Design

## Goal

Add live auto-refresh to the run detail page at `/runs/[runId]` so the page refreshes itself when the current run changes state, without polling and without requiring a manual browser refresh.

The refresh mechanism must use Server-Sent Events only.

## Scope

This feature applies only to the run detail page.

It does not change:

- the homepage
- the recent runs list
- project lists
- background polling behavior
- any other page

## Current State

- The backend already exposes `GET /api/runs/{run_id}/events/stream`.
- That stream currently replays all historical events for the run before subscribing to new ones.
- The run detail page currently loads run data once through `loadRun()` and then stays static.
- If the run advances to a new node status or a new top-level run state, the page does not update until the user reloads.

## Problem

If the frontend naively subscribes to the current SSE stream and refreshes on every relevant event, the initial connection will replay historical events and cause redundant page refreshes.

This means the missing piece is not just “subscribe to SSE”; it is “subscribe only to events newer than the snapshot the page already loaded.”

## Recommended Approach

Use SSE with an event-sequence cursor.

1. The page first loads the current run snapshot.
2. That snapshot includes the latest event sequence visible at load time.
3. The frontend opens an SSE connection with `after_sequence=<latest_event_sequence>`.
4. The backend streams only events newer than that sequence.
5. The frontend refreshes the run detail page only when the incoming event type is in a refresh whitelist.

This avoids replay-triggered refresh storms and keeps the implementation simple.

## API Design

### Run Detail Response

Extend `RunDetail` with:

- `latest_event_sequence: int = 0`

This value is the latest persisted event sequence for the run at the moment the run detail is serialized.

### SSE Stream Endpoint

Extend:

- `GET /api/runs/{run_id}/events/stream`

to accept:

- `after_sequence: int | None = None`

Behavior:

- if `after_sequence` is absent, preserve the current behavior
- if `after_sequence` is provided, replay only events with `sequence > after_sequence`
- after replaying filtered events, continue streaming new events as usual

## Refresh Whitelist

The frontend should refresh the page only for events that can change what the run detail page displays materially.

Refresh on:

- `cycle_started`
- `node_started`
- `node_completed`
- `node_failed`
- `clarification_required`
- `clarification_received`
- `approval_required`
- `approval_granted`
- `approval_rejected`
- `run_resumed`
- `run_completed`
- `quality_gate_passed`
- `quality_gate_failed`
- `delivery_completed`

Do not refresh on:

- `node_log`
- `context_indexed`
- `context_assembled`
- `checkpoint_saved`
- other purely diagnostic or intermediate events

## Frontend Behavior

### Subscription Lifecycle

Inside `/runs/[runId]`:

1. Run the normal initial `loadRun()`
2. Read `latest_event_sequence` from the loaded run snapshot
3. Open an `EventSource` to:
   - `/api/runs/{runId}/events/stream?after_sequence=<latest_event_sequence>`
4. Parse each incoming SSE message as an event payload
5. If the event type is in the whitelist, schedule a refresh
6. Close the stream on component unmount or when `runId` changes

### Refresh Coalescing

Multiple state-changing events can arrive in quick succession.

To avoid excessive API calls:

- debounce or coalesce refreshes into a short window, such as 150-250ms
- if a refresh is already scheduled or in flight, do not schedule another one immediately

This keeps the page responsive without hammering the backend.

### Connection State

The page should track a lightweight SSE connection state:

- `connecting`
- `connected`
- `disconnected`

This can be shown as a subtle status line in the run detail page, but it should not dominate the UI.

Recommended copy:

- `Live updates connected`
- `Live updates reconnecting`
- `Live updates disconnected`

## Backend Design

### Serialization

Add a serializer helper or extend the existing run-detail serializer so `RunDetail` includes:

- the maximum event sequence for the run

If the run has no events, return `0`.

### Stream Filtering

Update the event replay portion of the stream route so it can filter replayed events by sequence.

The live subscription path does not need structural changes.

The filtered replay logic should be the only new behavior.

## Frontend Design

### New Helper Module

Add a small helper module for run-detail event streaming rules, for example:

- `apps/web/lib/run-events.mjs`

Responsibilities:

- define the refresh whitelist
- expose a predicate like `shouldRefreshForRunEvent(type)`
- parse raw SSE payloads safely

### Run Detail Integration

Update the run detail page to:

- keep `loadRun()` reusable
- open the SSE stream after initial data load
- reconnect cleanly when `runId` changes
- schedule reloads through a coalesced refresh helper

No local incremental state patching is needed.

The page should keep using the backend as the source of truth.

## Error Handling

### SSE Parse Failures

If a single SSE message cannot be parsed:

- ignore that message
- do not tear down the whole subscription

### Connection Loss

If the browser disconnects from the event stream:

- mark the connection state as disconnected or reconnecting
- let `EventSource` handle built-in reconnection
- do not fall back to polling

### Refresh Failure

If `loadRun()` fails after an event-triggered refresh:

- preserve existing page state
- surface the existing run-detail error message
- keep the SSE connection alive unless the page is unmounting

## Testing Strategy

### Backend Tests

Add tests that verify:

- `RunDetail` includes `latest_event_sequence`
- the value is `0` when a run has no events
- `/events/stream?after_sequence=N` replays only newer events
- `/events/stream` without the query parameter preserves current replay behavior

### Frontend Tests

Add lightweight unit tests for:

- refresh-whitelist predicate
- ignoring non-refresh events
- refreshing on whitelisted events
- safe handling of malformed event payloads

For end-to-end verification in the current repo, `next build` must still pass after wiring the page to `EventSource`.

## File Impact

Expected backend files:

- `apps/api/app/models/schemas.py`
- `apps/api/app/api/serializers.py`
- `apps/api/app/api/routes.py`
- `apps/api/tests/test_clarification_api.py` or a new API test file if separation is cleaner

Expected frontend files:

- `apps/web/app/runs/[runId]/page.js`
- `apps/web/lib/run-events.mjs`
- `apps/web/lib/run-events.test.mjs`
- optionally `apps/web/app/globals.css` for the live-status indicator

## Non-Goals

- homepage live refresh
- polling fallback
- client-side state machine mirroring backend node transitions
- replacing the existing run detail fetch flow with fully streaming UI state

## Open Decisions Resolved

- refresh applies only to `/runs/[runId]`
- transport is SSE only
- refresh is triggered only by state-changing events
- initial replay must be filtered by event sequence to avoid duplicate refreshes
