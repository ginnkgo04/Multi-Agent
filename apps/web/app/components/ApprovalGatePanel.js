'use client';

import { useState } from 'react';

import { request } from '@/lib/api';
import {
  getApprovalActions,
  getApproveDialogConfig,
  getRejectApprovalDialogConfig,
} from '@/lib/approval.mjs';

function renderList(items, emptyLabel) {
  if (!items?.length) {
    return <div className="empty-state">{emptyLabel}</div>;
  }

  return (
    <ul className="clarification-list">
      {items.map((item, index) => (
        <li key={`${item}-${index}`}>{item}</li>
      ))}
    </ul>
  );
}

function renderInterfaceList(items) {
  if (!items?.length) {
    return <div className="empty-state">No interface contracts were included in the current plan.</div>;
  }

  return (
    <ul className="clarification-list">
      {items.map((item, index) => (
        <li key={`${item.name || item.path || 'interface'}-${index}`}>
          {item.name || item.path || JSON.stringify(item)}
        </li>
      ))}
    </ul>
  );
}

export default function ApprovalGatePanel({ pendingAction, runId, onSubmitted }) {
  const context = pendingAction?.approval_context || {};
  const [dialogMode, setDialogMode] = useState('');
  const [message, setMessage] = useState('');
  const [pending, setPending] = useState(false);
  const [error, setError] = useState('');

  const dialog =
    dialogMode === 'reject'
      ? getRejectApprovalDialogConfig()
      : dialogMode === 'approve'
        ? getApproveDialogConfig()
        : null;

  async function submitDecision() {
    if (!dialog) {
      return;
    }

    setPending(true);
    setError('');
    try {
      await request(`/runs/${runId}/approve`, {
        method: 'POST',
        body: JSON.stringify({
          approved: dialog.mode === 'approve',
          comment: dialog.requiresMessage ? message.trim() : '',
        }),
      });
      setDialogMode('');
      setMessage('');
      await onSubmitted();
    } catch (submitError) {
      setError(submitError.message);
      if (submitError.message.includes('Run is not waiting for approval')) {
        await onSubmitted();
      }
    } finally {
      setPending(false);
    }
  }

  return (
    <section className="panel panel-strong">
      <div className="topbar">
        <div>
          <div className="panel-title">Approval Gate</div>
          <div className="subtle">
            Review the current CA plan before implementation starts. Approve it to continue, or reject it with corrective feedback.
          </div>
        </div>
      </div>

      <div className="project-item" style={{ marginTop: 14 }}>
        <strong>Plan Summary</strong>
        <div className="subtle" style={{ marginTop: 8 }}>
          {context.summary || 'No approval summary has been captured yet.'}
        </div>
        <div className="subtle" style={{ marginTop: 8 }}>
          Plan kind: {context.plan_kind || 'initial'} | Approval state: {context.approval_state || 'pending'}
        </div>
      </div>

      <div className="clarification-grid">
        <div className="project-item">
          <strong>Architecture Decisions</strong>
          {renderList(context.architecture_decisions, 'No architecture decisions were recorded in the current plan.')}
        </div>
        <div className="project-item">
          <strong>Interfaces</strong>
          {renderInterfaceList(context.interfaces)}
        </div>
      </div>

      <div className="clarification-grid">
        <div className="project-item">
          <strong>Execution Contract</strong>
          <code className="artifact-preview" style={{ marginTop: 10 }}>
            {JSON.stringify(context.execution_contract || {}, null, 2)}
          </code>
        </div>
        <div className="project-item">
          <strong>Remediation Plan</strong>
          <code className="artifact-preview" style={{ marginTop: 10 }}>
            {JSON.stringify(context.remediation_plan || {}, null, 2)}
          </code>
        </div>
      </div>

      <div className="button-row" style={{ marginTop: 8 }}>
        {getApprovalActions().map((action) => (
          <button
            className={action.id === 'reject' ? 'button secondary' : 'button'}
            key={action.id}
            onClick={() => {
              setDialogMode(action.id);
              setError('');
            }}
            type="button"
          >
            {action.label}
          </button>
        ))}
      </div>

      {dialog ? (
        <div className="dialog-backdrop" role="presentation">
          <div aria-modal="true" className="dialog-card" role="dialog">
            <div className="panel-title">{dialog.title}</div>
            <div className="subtle">{dialog.description}</div>
            {dialog.requiresMessage ? (
              <div className="field">
                <label htmlFor="approval-feedback">Feedback</label>
                <textarea
                  id="approval-feedback"
                  onChange={(event) => setMessage(event.target.value)}
                  placeholder="Describe what CA should change before resubmitting the plan."
                  value={message}
                />
              </div>
            ) : null}
            {error ? <div className="notice">{error}</div> : null}
            <div className="button-row">
              <button
                className="button"
                disabled={pending || (dialog.requiresMessage && !message.trim())}
                onClick={submitDecision}
                type="button"
              >
                {pending ? 'Submitting...' : dialog.confirmLabel}
              </button>
              <button
                className="button secondary"
                disabled={pending}
                onClick={() => setDialogMode('')}
                type="button"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </section>
  );
}
