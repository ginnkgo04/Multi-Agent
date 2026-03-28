import StatusPill from './StatusPill';

export default function RunOverview({ run }) {
  if (!run) {
    return null;
  }

  const completedNodes = run.cycles.flatMap((cycle) => cycle.nodes).filter((node) => node.status === 'COMPLETED').length;
  const totalNodes = run.cycles.flatMap((cycle) => cycle.nodes).length;

  const metrics = [
    { label: 'Run Status', value: <StatusPill status={run.status} /> },
    { label: 'Current Cycle', value: <span className="metric-value">{run.current_cycle}</span> },
    { label: 'Max Cycles', value: <span className="metric-value">{run.max_cycles}</span> },
    { label: 'Node Progress', value: <span className="metric-value">{completedNodes}/{totalNodes || 6}</span> },
    { label: 'LLM Provider', value: <span className="metric-value">{run.provider_name}</span> },
    { label: 'Embedding Provider', value: <span className="metric-value">{run.embedding_provider_name}</span> },
  ];

  return (
    <>
      <div className="overview-grid">
        {metrics.map((metric) => (
          <div className="panel" key={metric.label}>
            <div className="metric-label">{metric.label}</div>
            <div>{metric.value}</div>
          </div>
        ))}
      </div>
      <div className="panel" style={{ marginTop: 18 }}>
        <div className="metric-label">Task Root</div>
        <code className="artifact-preview">{run.task_root_path}</code>
      </div>
    </>
  );
}
