import StatusPill from './StatusPill';

export default function CycleTimeline({ cycles }) {
  if (!cycles?.length) {
    return <div className="empty-state">No cycles recorded yet.</div>;
  }

  return (
    <div className="cycle-list">
      {cycles.map((cycle) => (
        <div className="cycle-card" key={cycle.id}>
          <div className="topbar">
            <div>
              <div className="panel-title">Cycle {cycle.cycle_index}</div>
              <div className="subtle">{cycle.remediation_requirement || 'Initial delivery cycle'}</div>
            </div>
            <StatusPill status={cycle.status} />
          </div>
          <div className="subtle" style={{ marginTop: 10 }}>
            Nodes: {cycle.nodes.map((node) => `${node.role}:${node.status}`).join(' · ')}
          </div>
          {cycle.quality_report ? (
            <div className="subtle" style={{ marginTop: 10 }}>
              QT {cycle.quality_report.status} | Defects: {cycle.quality_report.defect_list.length} | Retest: {cycle.quality_report.retest_scope.join(', ') || 'n/a'}
            </div>
          ) : null}
        </div>
      ))}
    </div>
  );
}
