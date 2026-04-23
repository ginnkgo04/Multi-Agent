import test from 'node:test';
import assert from 'node:assert/strict';

import {
  getClarificationActions,
  getRejectDialogConfig,
  shouldShowClarificationGate,
} from './clarification.mjs';

test('shouldShowClarificationGate only returns true for clarification actions', () => {
  assert.equal(shouldShowClarificationGate({ action_type: 'clarification' }), true);
  assert.equal(shouldShowClarificationGate({ action_type: 'approval' }), false);
});

test('getClarificationActions returns confirm and reject actions', () => {
  const actions = getClarificationActions();

  assert.deepEqual(actions.map((item) => item.id), ['accept_defaults', 'reject_defaults']);
});

test('getRejectDialogConfig marks textarea as required', () => {
  const dialog = getRejectDialogConfig();

  assert.equal(dialog.requiresMessage, true);
  assert.match(dialog.title, /Reject current default assumptions/i);
});
