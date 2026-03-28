export default function ArtifactPanel({ artifacts }) {
  if (!artifacts?.length) {
    return <div className="empty-state">Artifacts will appear here once agents start producing outputs.</div>;
  }

  return (
    <div className="artifact-list">
      {artifacts.map((artifact) => (
        <details className="artifact-item" key={artifact.id}>
          <summary>{artifact.name}</summary>
          <div className="subtle">{artifact.artifact_type} · {artifact.content_type}</div>
          <div className="subtle">{artifact.summary}</div>
          <div className="subtle">{artifact.path}</div>
          <code className="artifact-preview">{artifact.metadata?.content_preview || 'No preview available.'}</code>
        </details>
      ))}
    </div>
  );
}
