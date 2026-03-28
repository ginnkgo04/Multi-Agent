'use client';

import { useState } from 'react';
import { request } from '@/lib/api';

const initialForm = {
  name: 'Demo Workspace',
  description: 'Showcase workspace for multi-agent orchestration.',
  template: 'next-fastapi-template',
};

export default function CreateProjectForm({ onCreated }) {
  const [form, setForm] = useState(initialForm);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(event) {
    event.preventDefault();
    setPending(true);
    setError('');
    try {
      const created = await request('/projects', {
        method: 'POST',
        body: JSON.stringify(form),
      });
      onCreated?.(created);
      setForm(initialForm);
    } catch (submitError) {
      setError(submitError.message);
    } finally {
      setPending(false);
    }
  }

  return (
    <form className="form-grid" onSubmit={handleSubmit}>
      <div className="field">
        <label htmlFor="project-name">Project Name</label>
        <input
          id="project-name"
          value={form.name}
          onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
          required
        />
      </div>
      <div className="field">
        <label htmlFor="project-description">Description</label>
        <textarea
          id="project-description"
          value={form.description}
          onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))}
        />
      </div>
      <div className="button-row">
        <button className="button" type="submit" disabled={pending}>
          {pending ? 'Creating...' : 'Create Project'}
        </button>
      </div>
      {error ? <div className="notice">{error}</div> : null}
    </form>
  );
}
