import StatusPill from './StatusPill';

export default function GraphBoard({ graph }) {
  if (!graph?.nodes?.length) {
    return <div className="empty-state">The workflow graph will appear as soon as nodes are generated.</div>;
  }

  const latestCycle = Math.max(...graph.nodes.map((node) => node.cycle_index));
  const nodes = graph.nodes.filter((node) => node.cycle_index === latestCycle).sort((left, right) => left.batch_index - right.batch_index);

  return (
    <div className="graph-lane">
      {nodes.map((node) => {
        const className = ['graph-node'];
        if (node.status === 'FAILED' || node.status === 'FAILED_MAX_CYCLES') className.push('failed');
        if (node.status === 'BLOCKED') className.push('blocked');

        return (
          <div className={className.join(' ')} key={node.id}>
            <div className="graph-role">{node.role}</div>
            <div className="graph-cycle">Cycle {node.cycle_index}</div>
            <div className="graph-meta">
              <StatusPill status={node.status} />
            </div>
          </div>
        );
      })}
    </div>
  );
}
