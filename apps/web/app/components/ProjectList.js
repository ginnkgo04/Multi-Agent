export default function ProjectList({ projects }) {
  if (!projects.length) {
    return <div className="empty-state">No projects yet. Create one to start a run.</div>;
  }

  return (
    <div className="project-list">
      {projects.map((project) => (
        <div className="project-item" key={project.id}>
          <div className="panel-title">{project.name}</div>
          <div className="subtle">{project.description || 'No description provided.'}</div>
          <div className="subtle">Template: {project.template}</div>
        </div>
      ))}
    </div>
  );
}
