'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import CreateProjectForm from './components/CreateProjectForm';
import CreateRunForm from './components/CreateRunForm';
import ProjectList from './components/ProjectList';
import RunList from './components/RunList';
import { request } from '@/lib/api';

export default function HomePage() {
  const [projects, setProjects] = useState([]);
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  async function loadDashboard() {
    setLoading(true);
    setError('');
    try {
      const [projectResult, runResult] = await Promise.all([request('/projects'), request('/runs')]);
      setProjects(projectResult);
      setRuns(runResult);
    } catch (loadError) {
      setError(loadError.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  return (
    <main>
      <div className="page-shell">
        <section className="hero hero-grid">
          <div>
            <div className="kicker">White-Box AI Delivery</div>
            <h1>Build, observe, recover, and loop your software agents in public.</h1>
            <p>
              This dashboard turns a software request into an explicit PC / CA / approval / FD / BD / QT / DE workflow, then streams
              every event, artifact, retry, and remediation cycle. Each run writes concrete frontend and backend task files into its
              own workspace so you can inspect the generated implementation, not just the orchestration trace.
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
              <div className="project-item">6-role workflow with approval gates, clarification loops, and QT-driven remediation</div>
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
            <CreateProjectForm onCreated={loadDashboard} />
          </div>
        </section>

        <section className="dual-grid">
          <div className="panel">
            <div className="panel-title">Workspace Inventory</div>
            {loading ? <div className="empty-state">Loading projects...</div> : <ProjectList projects={projects} />}
            {error ? <div className="notice">{error}</div> : null}
          </div>
          <div className="panel">
            <div className="panel-title">Recent Runs</div>
            {loading ? <div className="empty-state">Loading runs...</div> : <RunList runs={runs.slice(0, 8)} />}
          </div>
        </section>
      </div>
    </main>
  );
}
