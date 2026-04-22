import test from 'node:test';
import assert from 'node:assert/strict';

import {
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

test('buildRunEventsUrl appends after_sequence when a cursor is present', () => {
  const url = buildRunEventsUrl('run-1', 7);

  assert.match(url, /\/runs\/run-1\/events\/stream\?after_sequence=7$/);
});
