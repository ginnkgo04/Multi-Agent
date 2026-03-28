'use client';

import Link from 'next/link';
import StatusPill from './StatusPill';

export default function RunList({ runs }) {
  if (!runs.length) {
    return <div className="empty-state">No runs yet. Start one from the launchpad.</div>;
  }

  return (
    <div className="project-list">
      {runs.map((run) => (
        <Link className="project-item run-item-link" href={`/runs/${run.id}`} key={run.id}>
          <div className="run-item-head">
            <div className="panel-title">Run {run.id.slice(0, 8)}</div>
            <StatusPill status={run.status} />
          </div>
          <div className="subtle run-requirement">{run.requirement}</div>
          <div className="subtle">Cycle {run.current_cycle} / {run.max_cycles}</div>
          <div className="subtle">Provider: {run.provider_name}</div>
        </Link>
      ))}
    </div>
  );
}
