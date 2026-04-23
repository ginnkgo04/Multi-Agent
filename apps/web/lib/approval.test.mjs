import test from 'node:test';
import assert from 'node:assert/strict';

import {
  getApprovalActions,
  getApproveDialogConfig,
  getRejectApprovalDialogConfig,
  shouldShowApprovalGate,
} from './approval.mjs';

test('shouldShowApprovalGate only returns true for approval actions', () => {
  assert.equal(shouldShowApprovalGate({ action_type: 'approval' }), true);
  assert.equal(shouldShowApprovalGate({ action_type: 'clarification' }), false);
});

test('getApprovalActions returns approve and reject actions', () => {
  const actions = getApprovalActions();

  assert.deepEqual(actions.map((item) => item.id), ['approve', 'reject']);
});

test('getApproveDialogConfig does not require a message', () => {
  const dialog = getApproveDialogConfig();

  assert.equal(dialog.requiresMessage, false);
  assert.match(dialog.title, /approve/i);
});

test('getRejectApprovalDialogConfig requires a message', () => {
  const dialog = getRejectApprovalDialogConfig();

  assert.equal(dialog.requiresMessage, true);
  assert.match(dialog.title, /reject/i);
});
