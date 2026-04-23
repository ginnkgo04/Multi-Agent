import test from 'node:test';
import assert from 'node:assert/strict';

import {
  RUN_EVENT_REFRESH_TYPES,
  buildRunEventsUrl,
  parseRunEventMessage,
  shouldRefreshForRunEvent,
} from './run-events.mjs';

test('shouldRefreshForRunEvent only returns true for state-changing events', () => {
  assert.equal(shouldRefreshForRunEvent('node_completed'), true);
  assert.equal(shouldRefreshForRunEvent('clarification_required'), true);
  assert.equal(shouldRefreshForRunEvent('node_log'), false);
  assert.equal(shouldRefreshForRunEvent('checkpoint_saved'), false);
});

test('parseRunEventMessage returns null for invalid SSE payloads', () => {
  assert.equal(parseRunEventMessage('{bad json'), null);
  assert.equal(parseRunEventMessage(JSON.stringify({ sequence: 3 })), null);
});

test('parseRunEventMessage returns parsed payloads with valid cursors', () => {
  const payload = { type: 'node_completed', sequence: 3, data: { id: 'n1' } };

  assert.deepEqual(parseRunEventMessage(JSON.stringify(payload)), payload);
});

test('parseRunEventMessage rejects non-integer cursor values', () => {
  assert.equal(parseRunEventMessage(JSON.stringify({ type: 'node_completed', sequence: -1 })), null);
  assert.equal(parseRunEventMessage(JSON.stringify({ type: 'node_completed', sequence: 1.5 })), null);
});

test('buildRunEventsUrl uses the base path without a cursor when none is present', () => {
  assert.equal(buildRunEventsUrl('run-1'), 'http://localhost:8000/api/runs/run-1/events/stream');
});

test('buildRunEventsUrl appends after_sequence when a cursor is present', () => {
  const url = buildRunEventsUrl('run-1', 7);

  assert.match(url, /\/runs\/run-1\/events\/stream\?after_sequence=7$/);
});

test('buildRunEventsUrl encodes reserved characters in the run id', () => {
  const url = buildRunEventsUrl('run/1?x=1', 7);

  assert.match(url, /\/runs\/run%2F1%3Fx%3D1\/events\/stream\?after_sequence=7$/);
});

test('RUN_EVENT_REFRESH_TYPES is exported as an immutable list', () => {
  assert.ok(Array.isArray(RUN_EVENT_REFRESH_TYPES));
  assert.equal(Object.isFrozen(RUN_EVENT_REFRESH_TYPES), true);
});
