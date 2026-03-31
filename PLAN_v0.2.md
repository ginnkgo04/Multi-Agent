# `v0.2` 详细实施计划：LangGraph 编排 + LangChain 单 Agent 落地

## Summary
- `v0.2` 的目标是把“项目确实基于 LangGraph / LangChain”落实到代码层，而不是只停留在依赖声明和项目描述。
- 编排层统一切到 `LangGraph`；单 Agent 层采用混合模式：
  - `PC / CA` 使用 `LangChain LCEL` 链式节点。
  - `FD / BD / DE / QT` 使用 `LangChain` 工具调用 Agent。
- 本版本不追求强自治或执行型工具，只做到“框架真实性 + 可运行 + 可恢复 + 可测试”。工具范围固定为平台内工具加 `RAG` 检索工具。

## Key Changes
### 1. 依赖与 Provider 接入
- 新增依赖：`langchain>=0.3`、`langchain-openai>=0.2`；保留现有 `langchain-core`、`langgraph`。
- `ProviderRegistry` 保持现有数据库配置模型不变，但新增两类解析方法：
  - `resolve_langchain_chat_model(session, name)`：返回 `ChatOpenAI`，使用现有 `base_url / api_key / model` 配置。
  - `resolve_langchain_embedding_model(session, name)`：返回 `OpenAIEmbeddings`，使用现有 embedding 配置。
- 现有自定义 `OpenAICompatibleChatProvider / EmbeddingProvider` 保留为兼容层和回退路径，但 `ExecutionRuntime` 的主执行路径不再直接调用它们。

### 2. LangGraph 编排替换
- 新增统一状态类型 `WorkflowState`，字段固定为：
  - `run_id`
  - `cycle_id`
  - `cycle_index`
  - `requirement`
  - `provider_name`
  - `embedding_provider_name`
  - `shared_plan_id`
  - `manual_approval`
  - `template_context`
  - `node_outputs`
  - `artifact_refs`
  - `last_completed_role`
  - `next_action`
  - `retry_counts`
  - `blocked_reason`
- 使用两张编排图，避免首轮和补救轮逻辑混杂：
  - `initial_graph`: `PC -> CA -> (FD || BD) -> DE -> QT`
  - `remediation_graph`: `CA -> (FD || BD) -> DE -> QT`
- `QT` 节点后使用条件边：
  - `PASS` -> 结束当前 run
  - `FAIL` -> 创建下一轮 `CycleRecord`，写入 remediation requirement，然后切换到 `remediation_graph`
- `ExecutionRuntime` 改成图执行适配层，只负责：
  - 初始化 `WorkflowState`
  - 调用对应 graph
  - 每个节点前后写 DB 状态和事件
  - 在 `QT FAIL` 时创建下一轮 cycle
  - 在恢复时从 checkpoint 重建 state 并续跑

### 3. 单 Agent 统一切到 LangChain
- `PC / CA` 使用 `LCEL`，实现固定为：
  - `ChatPromptTemplate`
  - `RunnableLambda` 组装输入
  - `ChatOpenAI.with_structured_output(PydanticSchema)`
- `PC` 和 `CA` 都必须有独立输出 schema，不再依赖自由 JSON 解析。
- `FD / BD / DE / QT` 使用工具调用 Agent，固定通过 `LangChain v1 create_agent` 运行，不允许继续直接拼 prompt 后让模型裸返回。
- 这 4 个角色统一使用以下工具集：
  - `get_requirement()`
  - `get_shared_plan()`
  - `list_upstream_artifacts()`
  - `retrieve_context(query, top_k=4)`：包装现有 `RagService.retrieve`
  - `emit_artifact(path, artifact_type, content_type, summary, content)`：写入当前节点的内存缓冲区
  - `submit_result(summary, handoff_notes, result_payload, confidence)`：结束当前节点并返回结构化结果
- 工具调用节点采用“缓冲后提交”模型：
  - `emit_artifact` 只写入当前节点的 `ExecutionBuffer`
  - 只有 `submit_result` 成功后，Runtime 才统一校验并落库产物
  - 节点结束条件固定为：至少调用一次 `submit_result`
- `ExecutionBuffer` 必须保存：
  - `artifacts`
  - `result_payload`
  - `handoff_notes`
  - `confidence`
  - `tool_trace`
- 角色分工固定如下：
  - `PC`：输出 requirement brief、acceptance criteria、work breakdown
  - `CA`：输出 shared plan、contracts、task graph
  - `FD`：通过工具生成 frontend 产物
  - `BD`：通过工具生成 backend 产物
  - `DE`：通过工具整合交付产物
  - `QT`：通过工具生成质量报告并明确 `PASS/FAIL`

### 4. RAG 在 v0.2 的落地方式
- `v0.2` 不重写存储层，继续复用当前 `KnowledgeChunkRecord + RagService`。
- 但 `RAG` 不再只作为后台隐式上下文，而是显式成为 Agent 可调用工具：
  - `retrieve_context(query, top_k)` 直接进入 `FD / BD / DE / QT` 的工具集。
- `PC / CA` 继续沿用当前 `ContextAssembler` 的静态上下文拼装，不走工具调用。
- `FD / BD / DE / QT` 的输入上下文固定拆成两层：
  - 基础上下文：requirement、shared plan、依赖产物摘要、recent memories
  - 动态上下文：由 `retrieve_context` 工具按需拉取
- `v0.2` 不做自动产物入库检索增强，也不做长期记忆重构；这些留在 `v0.3`。

### 5. Checkpoint 与恢复
- 新增 `RunCheckpointRecord`，字段固定为：
  - `id`
  - `run_id`
  - `cycle_id`
  - `cycle_index`
  - `graph_kind`
  - `last_completed_role`
  - `serialized_state`
  - `created_at`
- 每当一个节点成功完成时，保存一条 checkpoint。
- 每当 `QT FAIL` 生成下一轮 cycle 时，再额外保存一条 cycle 切换 checkpoint。
- `/runs/{id}/resume` 的行为固定为：
  - 只允许恢复 `BLOCKED` run
  - 读取当前 cycle 的最新 checkpoint
  - 重建 `WorkflowState`
  - 从 `last_completed_role` 的下一节点继续，不重跑已完成节点
- 本版本不使用 LangGraph 官方 checkpointer，避免引入额外持久化栈；checkpoint 由应用层 DB 表统一管理。

## Public Interfaces / Type Changes
- HTTP 路径保持不变：
  - `POST /runs`
  - `GET /runs/{id}`
  - `GET /runs/{id}/graph`
  - `POST /runs/{id}/resume`
  - `GET /runs/{id}/events/stream`
- `RunRead` 和 `RunDetail` 字段本版本不强制变更，避免前端联调成本扩大。
- 新增内部类型：
  - `WorkflowState`
  - `ExecutionBuffer`
  - `RunCheckpointRecord`
  - `PCResultSchema`
  - `CAResultSchema`
  - `ToolAgentSubmitPayload`
- `AgentTaskContext` 新增但只新增两项，不重构全体字段：
  - `template_context`
  - `shared_plan_id`
- 事件模型新增但只补最少集合：
  - `NODE_LOG`
  - `CHECKPOINT_SAVED`
- `NODE_LOG` 必须在工具调用 Agent 的每次工具执行后发布，内容至少包含 `tool_name` 和 `status`。

## Test Plan
- 编排测试：
  - 首轮 graph 编译后路径必须为 `PC -> CA -> FD/BD -> DE -> QT`
  - 补救轮 graph 编译后不得包含 `PC`
  - `FD` 与 `BD` 必须属于并行分支
- LCEL 测试：
  - `PC` 节点返回结构化 schema，缺字段时报错
  - `CA` 节点返回 `shared_plan` 并可持久化
- Tool Agent 测试：
  - `FD / BD / DE / QT` 能通过工具生成至少一个 artifact 并成功 `submit_result`
  - 未调用 `submit_result` 时节点必须失败
  - `retrieve_context` 工具能正确包装 `RagService.retrieve`
- 恢复测试：
  - 在 `FD` 或 `BD` 失败后，`resume` 只能从失败节点所在阶段继续
  - 已完成节点不会被重复写 artifact
- 回归测试：
  - 现有创建 run、查看 graph、查看 artifact、SSE 流仍可工作
  - `QT FAIL` 仍会创建下一轮 cycle 并从 `CA` 开始

## Assumptions
- `v0.2` 仅支持现有 `openai-compatible` provider 体系，不扩展多厂商适配层。
- `FD / BD / DE / QT` 的工具调用只面向平台内部能力，不加入 shell、测试执行、代码运行工具。
- `PC / CA` 不使用工具调用 Agent 执行器，只使用 LCEL，保证实现简单且答辩时口径清晰。
- `RAG` 在 `v0.2` 只作为工具化检索能力接入，不在本版本实现自动索引产物、长期记忆分层和统一上下文仓库。
- 现有数据库和前端页面保持兼容优先；`v0.2` 不做大规模页面重构，只保证数据层和运行路径真实切到 LangGraph / LangChain。
