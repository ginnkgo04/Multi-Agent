# Run Workspace Incremental Editing Design

## Goal

Change the orchestration runtime so that each run keeps one stable code workspace and one stable delivery directory at the run root:

- `tasks/<run_id>/workspace/frontend`
- `tasks/<run_id>/workspace/backend`
- `tasks/<run_id>/delivery`

After `QT` rejects a cycle and the workflow returns to `CA`, later `FD` and `BD` executions must perform true incremental edits against the existing run workspace instead of creating a new per-cycle code directory.

This change must support:

- creating new files
- modifying existing files in place
- deleting obsolete files

For existing files, the system must forbid whole-file overwrite behavior. Updates must use minimal edit operations only.

## Scope

This design changes only the code-generation and delivery workspace model for new runs.

It does not change:

- the workflow order `PC -> CA -> FD + BD -> QT -> DE`
- optional execution of only `FD` or only `BD`
- old run compatibility or migration
- cycle count behavior
- approval or clarification semantics

## Current State

- `ArtifactStore` writes every artifact under `cycles/cycle-xx/`.
- `FD` and `BD` currently generate source files under:
  - `cycles/cycle-xx/workspace/frontend`
  - `cycles/cycle-xx/workspace/backend`
- `DE` currently writes delivery artifacts under `cycles/cycle-xx/delivery`.
- `ContextAssembler` builds `upstream_artifacts` only from nodes inside the current cycle dependency chain.
- `FD`, `BD`, `QT`, and `DE` therefore do not receive the current run workspace as an explicit editable baseline.
- The current file-generation prompts are file-content oriented: the model can regenerate a target file and save it, but there is no first-class concept of incremental edit operations.
- The current artifact save path supports writing files only. It has no delete action.

This means remediation cycles can reuse intent and plan context, but they do not perform true codebase evolution against one persistent workspace.

## Target Directory Model

For every new run:

- `tasks/<run_id>/input/`
- `tasks/<run_id>/logs/`
- `tasks/<run_id>/workspace/frontend/`
- `tasks/<run_id>/workspace/backend/`
- `tasks/<run_id>/delivery/`
- `tasks/<run_id>/cycles/cycle-xx/requirements/`
- `tasks/<run_id>/cycles/cycle-xx/architecture/`
- `tasks/<run_id>/cycles/cycle-xx/quality/`
- `tasks/<run_id>/cycles/cycle-xx/implementation/frontend/`
- `tasks/<run_id>/cycles/cycle-xx/implementation/backend/`

Directory semantics:

- `workspace/frontend` and `workspace/backend` are the only live code directories for the run.
- `delivery` is the only final delivery directory for the run.
- `cycles/cycle-xx/*` contain process artifacts only.
- No cycle may create `cycles/cycle-xx/workspace/*`.
- No cycle may create `cycles/cycle-xx/delivery/*`.

## Required Runtime Behavior

### First Cycle

- `FD` writes frontend code into `tasks/<run_id>/workspace/frontend/`.
- `BD` writes backend code into `tasks/<run_id>/workspace/backend/`.
- `QT` validates the run-level workspace.
- `DE` assembles final outputs into `tasks/<run_id>/delivery/`.

### Remediation Cycle

- `CA` produces a remediation-oriented shared plan for the next cycle.
- `FD` and `BD` must edit the existing run-level workspace in place.
- `QT` validates the updated run-level workspace.
- `DE` writes the latest delivery outputs to the same run-level `delivery/` directory.

The remediation cycle must evolve the same codebase instead of generating a new code tree.

## True Incremental Editing Requirements

True incremental editing means the system behaves as a patching engine, not as a repeated full-file generator.

For each existing file:

- the system reads the current file contents before planning edits
- the model receives the current file contents or relevant anchored sections as explicit context
- the model emits edit operations against the existing file
- the runtime validates those operations against the current file state before applying them

For each new file:

- the model may emit a create operation with full file contents

For each obsolete file:

- the model may emit a delete operation

For existing files, the runtime must reject any update path that effectively clears the file and rewrites the whole file as raw replacement content.

## Editing Architecture

The editing flow should follow the same mature shape used by patch-oriented coding systems.

### 1. Context Selector

For `FD`, `BD`, `QT`, and `DE`, the runtime must explicitly gather the current run workspace baseline:

- workspace file manifest for the owned tree
- current contents for files targeted by the edit plan
- targeted anchors or narrowed sections for large files
- current CA shared plan and remediation plan
- current quality defects and fix guidance when present

This baseline is separate from the existing per-cycle upstream artifact chain.

### 2. Edit Planner

`FD` and `BD` must stop returning only a list of final artifact contents for existing files.

Instead, they must produce an edit plan composed of operations:

- `create`
- `update`
- `delete`

Each operation must include enough information for deterministic application and validation.

Suggested operation shape:

```json
{
  "path": "workspace/frontend/app/page.tsx",
  "operation": "update",
  "strategy": "patch",
  "summary": "Update hero copy and CTA layout",
  "anchors": ["export default function Page()", "<main"],
  "old_text": "optional exact text for replace strategy",
  "new_text": "optional replacement text for replace strategy",
  "unified_diff": "optional unified diff for patch strategy"
}
```

Delete example:

```json
{
  "path": "workspace/frontend/components/LegacyBanner.tsx",
  "operation": "delete",
  "summary": "Remove deprecated banner component"
}
```

Create example:

```json
{
  "path": "workspace/backend/app/validators.py",
  "operation": "create",
  "summary": "Add request validation helpers",
  "content": "full file content"
}
```

### 3. Edit Strategy

Allowed strategies for existing files:

- exact replace with `old_text -> new_text`
- anchored insert
- anchored delete
- unified diff / patch

Allowed strategy for new files:

- full file create

Disallowed for existing files:

- raw whole-file rewrite
- delete-all-then-replace disguised as an update

Recommended routing:

- small localized change: exact replace or anchored insert/delete
- medium structured change: unified diff / patch
- new file: create
- removed file: delete

There is no whole-file rewrite fallback for existing files.

## Prompt Contract Changes

### FD and BD

`FD` and `BD` prompts must include explicit workspace-baseline sections, not only artifact previews.

Required prompt sections:

- `CURRENT_WORKSPACE_MANIFEST`
- `TARGET_FILE_PATH`
- `TARGET_FILE_EXISTS`
- `EXISTING_FILE_CONTENT` for updates
- `EDIT_CONSTRAINTS`
- `RESOLVED_EXECUTION_CONFIG_JSON`
- `SHARED_PLAN_JSON`
- `QUALITY_DEFECTS_JSON` when running after failed `QT`

Required edit constraints:

- modify existing files in place
- do not regenerate a parallel directory structure
- do not overwrite an existing file with a full rewritten file body
- prefer the smallest valid edit operation
- delete files explicitly when removal is required

### QT and DE

`QT` and `DE` must inspect the run-level workspace:

- `QT` validates `tasks/<run_id>/workspace/frontend` and `tasks/<run_id>/workspace/backend`
- `DE` packages output from the same workspace into `tasks/<run_id>/delivery`

Defect locations and delivery references must use run-level workspace paths such as:

- `workspace/frontend/app/page.tsx`
- `workspace/backend/app/routes.py`

## Validation Guardrails

The runtime must validate edit operations before applying them.

### Update Validation

For `update` operations:

- target path must already exist
- exact-replace operations must match current `old_text`
- anchored operations must match their anchors
- unified diffs must apply cleanly to the current file contents

### Rewrite Prevention

For existing files, reject the operation if:

- the system tries to write raw full-file content without a patch/edit primitive
- the update replaces essentially the full file body instead of a localized region
- the operation removes all previous content and inserts a new full body as one update

The runtime should treat that as invalid edit planning and force a replanning pass with fresh file context.

### Delete Validation

For `delete` operations:

- target path must exist
- delete must be explicit
- delete must remove the file from disk
- delete should produce a stored artifact/event record describing the deletion

### Create Validation

For `create` operations:

- target path must not already exist unless the operation is reclassified as update
- content must be complete and valid for the file type

## Storage Routing

`ArtifactStore` must route outputs by path class.

Run-level outputs:

- `workspace/frontend/*`
- `workspace/backend/*`
- `delivery/*`

These write under `task_root(run_id)`.

Cycle-level outputs:

- `requirements/*`
- `architecture/*`
- `quality/*`
- `implementation/frontend/*`
- `implementation/backend/*`

These write under `cycle_root(run_id, cycle_index)`.

The save layer must support:

- create file
- patch existing file
- delete file
- record each operation in artifact metadata

Artifact metadata for update and delete operations should include:

- `operation`
- `path_class`
- `base_file_present`
- `edit_strategy`
- `change_summary`

## Context Assembly Changes

`ContextAssembler` needs a second source of truth beyond per-cycle upstream artifacts.

For `FD`, `BD`, `QT`, and `DE`, it must gather:

- run-level workspace manifests
- relevant current file contents
- cycle-local process artifacts
- retrieved knowledge/context documents
- shared plan and remediation plan
- cycle summaries and recent memories

This means:

- existing `_artifact_manifests()` behavior remains useful for cycle-local artifacts
- new workspace-baseline collection must be added explicitly
- remediation work can no longer rely on RAG snippets alone for code context

The returned task context should include dedicated fields for:

- workspace file manifest
- editable file snapshots
- deletion candidates when referenced by the plan or defects

## Data Model Changes

The runtime needs explicit edit-operation models.

Suggested additions:

- `WorkspaceFileSnapshot`
- `EditOperation`
- `EditPlan`

Suggested `EditOperation` schema fields:

- `path`
- `operation`
- `strategy`
- `summary`
- `content`
- `old_text`
- `new_text`
- `anchors`
- `unified_diff`

`AgentTaskResult` for `FD` and `BD` should carry both:

- cycle-level documentation artifacts such as `implementation/.../notes.md`
- structured edit operations for workspace mutations

## Non-Goals

This design does not require:

- migrating or repairing old runs
- preserving old cycle workspaces
- storing a full workspace snapshot for every cycle
- implementing partial execution of only `FD` or only `BD`

## File Impact

Expected backend files:

- `apps/api/app/services/artifact_store.py`
- `apps/api/app/services/context_assembler.py`
- `apps/api/app/agents/base.py`
- `apps/api/app/agents/runtime_types.py`
- `apps/api/app/agents/langchain_agents.py`
- `apps/api/app/models/schemas.py`
- `apps/api/app/services/requirement_intake.py`

Expected tests:

- `apps/api/tests/test_artifact_store.py`
- `apps/api/tests/test_context_pipeline.py`
- `apps/api/tests/test_agent_format_normalization.py`
- `apps/api/tests/test_execution_runtime_graph.py`

## Testing Strategy

### Artifact Routing

Verify:

- `workspace/frontend/*` writes under `tasks/<run_id>/workspace/frontend/*`
- `workspace/backend/*` writes under `tasks/<run_id>/workspace/backend/*`
- `delivery/*` writes under `tasks/<run_id>/delivery/*`
- `requirements/*`, `architecture/*`, `quality/*`, and `implementation/*` remain cycle-scoped

### True Incremental Updates

Verify:

- an existing file update is applied as an edit operation, not a raw overwrite
- update validation fails when `old_text` or patch context no longer matches
- an attempted whole-file rewrite of an existing file is rejected
- remediation cycle writes to the same run workspace used by cycle 1

### File Deletion

Verify:

- an explicit delete operation removes the target file
- delete fails when the file does not exist
- delete is recorded in artifact metadata

### QT and DE Baseline Usage

Verify:

- `QT` reads the run-level workspace rather than any cycle-local workspace
- `DE` reads the run-level workspace and writes to run-level `delivery`
- reported defect locations use `workspace/...` paths

### Intake and Documentation

Verify:

- generated task README documents the new run-level workspace and delivery layout
- no new run mentions `cycles/cycle-xx/workspace/*` as the canonical code location

## Acceptance Criteria

The design is successful when a new run behaves like this:

1. Cycle 1 creates code in `tasks/<run_id>/workspace/...`.
2. `QT` fails and sends the run back to `CA`.
3. Cycle 2 `FD` and `BD` modify the same files in the same `workspace/...` tree using explicit edit operations.
4. If a file is no longer needed, the cycle can delete it explicitly.
5. Existing files are never updated by blanking and rewriting the full file body.
6. `DE` publishes final outputs under `tasks/<run_id>/delivery/...`.
