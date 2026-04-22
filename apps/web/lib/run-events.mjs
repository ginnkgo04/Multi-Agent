import { API_BASE } from './api.js';

const RUN_EVENT_REFRESH_TYPES = new Set([
  'cycle_started',
  'node_started',
  'node_completed',
  'node_failed',
  'clarification_required',
  'clarification_received',
  'approval_required',
  'approval_granted',
  'approval_rejected',
  'run_resumed',
  'run_completed',
  'quality_gate_passed',
  'quality_gate_failed',
  'delivery_completed',
]);

function shouldRefreshForRunEvent(type) {
  return RUN_EVENT_REFRESH_TYPES.has(type);
}

function parseRunEventMessage(raw) {
  try {
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed.type !== 'string' || typeof parsed.sequence !== 'number') {
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
}

function buildRunEventsUrl(runId, latestEventSequence) {
  const params = new URLSearchParams();
  if (Number.isFinite(latestEventSequence) && latestEventSequence > 0) {
    params.set('after_sequence', String(latestEventSequence));
  }
  const suffix = params.toString() ? `?${params.toString()}` : '';
  return `${API_BASE}/runs/${runId}/events/stream${suffix}`;
}

export {
  RUN_EVENT_REFRESH_TYPES,
  buildRunEventsUrl,
  parseRunEventMessage,
  shouldRefreshForRunEvent,
};
