'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { request } from '@/lib/api';

export default function CreateRunForm({ projects }) {
  const router = useRouter();
  const defaultProject = useMemo(() => projects?.[0]?.id || '', [projects]);
  const [form, setForm] = useState({
    project_id: defaultProject,
    requirement: 'Build a multi-agent dashboard that supports live observability, retry recovery, and QT remediation loops for a web feature workflow.',
  });
  const [pending, setPending] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!form.project_id && defaultProject) {
      setForm((current) => ({ ...current, project_id: defaultProject }));
    }
  }, [defaultProject, form.project_id]);

  async function handleSubmit(event) {
    event.preventDefault();
    setPending(true);
    setError('');
    try {
      const created = await request('/runs', {
        method: 'POST',
        body: JSON.stringify(form),
      });
      router.push(`/runs/${created.id}`);
    } catch (submitError) {
      setError(submitError.message);
    } finally {
      setPending(false);
    }
  }

  return (
    <form className="form-grid" onSubmit={handleSubmit}>
      <div className="field">
        <label htmlFor="run-project">Project</label>
        <select
          id="run-project"
          value={form.project_id || defaultProject}
          onChange={(event) => setForm((current) => ({ ...current, project_id: event.target.value }))}
          required
        >
          <option value="">Select a project</option>
          {projects.map((project) => (
            <option key={project.id} value={project.id}>
              {project.name}
            </option>
          ))}
        </select>
      </div>
      <div className="field">
        <label htmlFor="requirement">Requirement</label>
        <textarea
          id="requirement"
          value={form.requirement}
          onChange={(event) => setForm((current) => ({ ...current, requirement: event.target.value }))}
          required
        />
      </div>
      <div className="button-row">
        <button className="button" type="submit" disabled={pending || !projects.length}>
          {pending ? 'Launching...' : 'Start Run'}
        </button>
      </div>
      <div className="subtle">Each run creates a real task workspace under `tasks/&lt;run_id&gt;/cycles/` with generated frontend, backend, quality, and post-QT delivery files.</div>
      {error ? <div className="notice">{error}</div> : null}
      {!projects.length ? <div className="notice">Create a project first so the orchestrator has a workspace.</div> : null}
    </form>
  );
}
