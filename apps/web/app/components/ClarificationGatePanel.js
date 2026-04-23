'use client';

import { useState } from 'react';

import { request } from '@/lib/api';
import {
  getClarificationActions,
  getConfirmDialogConfig,
  getRejectDialogConfig,
} from '@/lib/clarification.mjs';

function renderList(items, emptyLabel, ordered = false) {
  if (!items?.length) {
    return <div className="empty-state">{emptyLabel}</div>;
  }

  const ListTag = ordered ? 'ol' : 'ul';
  return (
    <ListTag className="clarification-list">
      {items.map((item, index) => (
        <li key={`${item}-${index}`}>{item}</li>
      ))}
    </ListTag>
  );
}

export default function ClarificationGatePanel({ pendingAction, runId, onSubmitted }) {
  const context = pendingAction?.clarification_context || {};
  const [dialogMode, setDialogMode] = useState('');
  const [message, setMessage] = useState('');
  const [pending, setPending] = useState(false);
  const [error, setError] = useState('');

  const dialog =
    dialogMode === 'reject_defaults'
      ? getRejectDialogConfig()
      : dialogMode === 'accept_defaults'
        ? getConfirmDialogConfig()
        : null;

  async function submitDecision() {
    if (!dialog) {
      return;
    }

    setPending(true);
    setError('');
    try {
      await request(`/runs/${runId}/clarify`, {
        method: 'POST',
        body: JSON.stringify({
          decision: dialog.mode,
          message: dialog.requiresMessage ? message : '',
          structured_context: {},
        }),
      });
      setDialogMode('');
      setMessage('');
      await onSubmitted();
    } catch (submitError) {
      setError(submitError.message);
      if (submitError.message.includes('Run is not waiting for clarification')) {
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
          <div className="panel-title">Clarification Gate</div>
          <div className="subtle">
            Review the planner&apos;s current assumptions, then continue with them or reject them with corrective feedback.
          </div>
        </div>
      </div>

      <div className="project-item" style={{ marginTop: 14 }}>
        <strong>Current Understanding</strong>
        <div className="subtle" style={{ marginTop: 8 }}>
          {context.requirement_brief || 'No planner brief has been captured yet.'}
        </div>
      </div>

      <div className="clarification-grid">
        <div className="project-item">
          <strong>Default Assumptions</strong>
          {renderList(context.assumed_defaults, 'No default assumptions captured yet.')}
        </div>
        <div className="project-item">
          <strong>Questions to Resolve</strong>
          {renderList(context.clarifying_questions, 'No clarification questions captured yet.', true)}
        </div>
      </div>

      <div className="clarification-grid">
        <div className="project-item">
          <strong>Plan Draft</strong>
          <code className="artifact-preview" style={{ marginTop: 10 }}>
            {JSON.stringify(context.acceptance_criteria || {}, null, 2)}
          </code>
          {renderList(context.work_breakdown, 'No work breakdown captured yet.')}
        </div>
        <div className="project-item">
          <strong>Recent Feedback</strong>
          {renderList(
            (context.clarification_history || []).slice(-3).reverse().map((item) => item.message),
            'No clarification feedback has been submitted yet.',
          )}
        </div>
      </div>

      <div className="button-row" style={{ marginTop: 8 }}>
        {getClarificationActions().map((action) => (
          <button
            className={action.id === 'reject_defaults' ? 'button secondary' : 'button'}
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
                <label htmlFor="clarification-feedback">Feedback</label>
                <textarea
                  id="clarification-feedback"
                  onChange={(event) => setMessage(event.target.value)}
                  placeholder="Describe which assumptions are incorrect and how the planner should adjust."
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
