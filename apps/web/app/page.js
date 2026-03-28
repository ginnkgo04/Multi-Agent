'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import CreateProjectForm from './components/CreateProjectForm';
import CreateRunForm from './components/CreateRunForm';
import ProjectList from './components/ProjectList';
import { request } from '@/lib/api';

export default function HomePage() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  async function loadProjects() {
    setLoading(true);
    setError('');
    try {
      const result = await request('/projects');
      setProjects(result);
    } catch (loadError) {
      setError(loadError.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadProjects();
  }, []);

  return (
    <main>
      <div className="page-shell">
        <section className="hero hero-grid">
          <div>
            <div className="kicker">White-Box AI Delivery</div>
            <h1>Build, observe, recover, and loop your software agents in public.</h1>
            <p>
              This dashboard turns a software request into an explicit PC / CA / FD / BD / DE / QT workflow, then streams every event,
              artifact, retry, and remediation cycle. Each run now writes concrete frontend and backend task files into its own
              workspace so you can inspect the generated implementation, not just the orchestration trace.
            </p>
            <div className="button-row">
              <Link className="button" href="#launchpad">Jump to Launchpad</Link>
              <a className="button secondary" href="http://localhost:8000/api/health" target="_blank" rel="noreferrer">
                API Health
              </a>
            </div>
          </div>
          <div className="panel panel-strong">
            <div className="panel-title">Platform Highlights</div>
            <div className="project-list">
              <div className="project-item">6-role workflow with explicit graph batches and QT remediation loops</div>
              <div className="project-item">Persistent runs, cycles, nodes, artifacts, events, and memory traces</div>
              <div className="project-item">Live LLM and embedding calls powered by the API keys configured in `apps/api/.env`</div>
            </div>
          </div>
        </section>

        <section className="dashboard-grid" id="launchpad">
          <div className="panel panel-strong">
            <div className="panel-title">Run Launchpad</div>
            <div className="subtle" style={{ marginBottom: 14 }}>
              Choose a project, submit a requirement, and let the platform generate real task files under the dedicated `tasks/` workspace for each run.
            </div>
            <CreateRunForm projects={projects} />
          </div>
          <div className="panel">
            <div className="panel-title">Create Project</div>
            <CreateProjectForm onCreated={loadProjects} />
          </div>
        </section>

        <section className="dual-grid">
          <div className="panel">
            <div className="panel-title">Workspace Inventory</div>
            {loading ? <div className="empty-state">Loading projects...</div> : <ProjectList projects={projects} />}
            {error ? <div className="notice">{error}</div> : null}
          </div>
          <div className="panel">
            <div className="panel-title">How To Inspect Real Outputs</div>
            <div className="project-list">
              <div className="project-item">1. Start a run and open the live dashboard.</div>
              <div className="project-item">2. Watch artifacts appear by cycle as frontend, backend, delivery, and quality files.</div>
              <div className="project-item">3. Open the task root path from the run overview to inspect the generated implementation workspace.</div>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
