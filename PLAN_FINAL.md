# 多 Agent 平台课程项目版迭代计划（4 个版本）

**摘要**
- 目标版本定位为“课程项目版”，优先补齐“描述里写了、实现里要真实存在”的能力，再补可观测和流程控制。
- 迭代顺序固定为 `v0.2 编排真实性` -> `v0.3 上下文链路` -> `v0.4 白盒观测` -> `v1.0 流程闭环`，每个版本按 1 周开发 + 0.5 周联调验收安排。
- 交付标准不是做成生产级平台，而是让 LangGraph、RAG、长期记忆、共享计划、审批控制、白盒看板都在当前仓库中有真实、可演示、可测试的落地实现。

**版本计划**
1. `v0.2` 真实编排替换版  
将当前自研 `while + batch scheduler` 运行时替换为真实 LangGraph 执行图，但保留现有 6 角色和对外 REST 接口。  
定义统一 `WorkflowState`，字段固定为：`run_id`、`cycle_id`、`cycle_index`、`current_role`、`shared_plan_id`、`context_ids`、`last_result`、`retry_count`、`approval_required`、`blocked_reason`。  
用 LangGraph 建图表达 `PC -> CA -> FD/BD 并行 -> DE -> QT`，并用条件边表达 `QT=PASS` 结束、`QT=FAIL` 生成下一 cycle 并从 `CA` 重新进入。  
`ExecutionRuntime` 改为图执行适配层，只负责启动、恢复、取消和 DB 落库，不再负责手写批次循环。  
新增运行检查点持久化表，按“每个节点完成后”保存图状态；`/runs/{id}/resume` 必须从最新 checkpoint 恢复，只重跑未完成节点。  
保留现有 `RunRecord/CycleRecord/NodeExecutionRecord`，避免前端和现有查询接口大改。  
验收标准：仓库中出现真实 `langgraph` import 和 StateGraph 编排代码；现有流程仍可跑通；QT 失败时能自动进入下一轮并从 `CA` 开始。

2. `v0.3` 上下文工程与 RAG 强化版  
把当前 `KnowledgeChunkRecord` 扩展为统一上下文文档层，新增 `ContextDocumentRecord`，来源固定支持：`knowledge`、`artifact`、`shared_plan`、`memory`、`requirement`。  
节点产物保存后自动入库为可检索文档，不再依赖手动 `/knowledge/ingest` 才能形成完整上下文；手动导入接口保留，仅作为外部知识补充入口。  
新增独立 `SharedPlanRecord`，由 `PC` 产出初版、`CA` 更新结构化计划；后续角色只读这个计划对象，不再从 `result_payload` 临时抽取。  
长期记忆改成两层：`MemoryRecord` 保存原始短记忆，`MemorySummaryRecord` 保存每轮结束后的压缩摘要；上下文组装时固定顺序为 `requirement -> shared_plan -> upstream_artifacts -> retrieved_docs -> cycle_summaries -> recent_memories`。  
检索返回结构统一为 `source_type`、`source_id`、`path`、`score`、`excerpt`、`metadata`，并在 `AgentTaskContext` 中显式传递 `context_sources`。  
新增自动上下文预算策略：优先共享计划和本轮依赖产物，其次检索文档，最后 recent memories；超预算时先裁剪 memories，再裁剪低分检索结果。  
验收标准：不手动导入也能检索到本轮产物和共享计划；`shared_plan` 有独立持久化对象；任一节点上下文都能追溯来源。

3. `v0.4` 白盒可观测增强版  
事件模型扩展为：`NODE_LOG`、`CONTEXT_RESOLVED`、`PROMPT_BUILT`、`MODEL_CALL_STARTED`、`MODEL_CALL_FINISHED`、`ARTIFACT_INDEXED`、`APPROVAL_REQUIRED`、`APPROVAL_GRANTED`。  
新增 `PromptTraceRecord` 和 `ModelCallRecord`，存储每次调用的系统提示词、用户提示词、上下文来源列表、开始时间、结束时间、耗时、模型名、usage；若 provider 不返回 token usage，则字段存 `null`。  
后端在“组装上下文”“构造 prompt”“发起模型调用”“写入结果”“索引产物”五个阶段都要发事件，SSE 保持单通道，不拆新协议。  
前端运行页改为展示完整多 cycle DAG，不再只显示最新 cycle；节点点击后展开节点详情，固定展示状态、重试次数、错误、上下文来源、prompt 摘要、模型调用耗时、产物列表。  
事件流页面改为类型化渲染，不再只打印原始 JSON；至少对 `NODE_LOG`、`MODEL_CALL_FINISHED`、`APPROVAL_REQUIRED` 做专门展示。  
把当前未使用的 `CycleTimeline` 接入运行详情页，展示每轮 remediation 和 QT 结果。  
验收标准：一次完整运行中，用户可从前端追溯“某个节点用了什么上下文、发了什么 prompt、何时调用模型、产出了什么文件、为什么失败”。

4. `v1.0` 流程闭环与字段生效版  
`manual_approval=true` 时，在每个 cycle 的 `CA` 完成后进入审批门，暂停在 `WAITING_APPROVAL`，只有审批通过才允许进入 `FD/BD`；`manual_approval=false` 保持自动流转。  
新增 `ApprovalRecord`，记录审批轮次、审批人、审批意见、时间；课程项目版默认单用户，审批人字段可直接记录固定字符串 `local-user`。  
新增 `POST /runs/{id}/approve` 接口，载荷固定为 `approved: bool` 和 `comment: str`；拒绝审批时，当前 cycle 进入 `BLOCKED`，允许修改需求后手动恢复。  
`template_context` 从占位字段升级为真实输入，固定注入到 `PC` 和 `CA` prompt，并在共享计划中落库，供后续角色只读引用。  
恢复逻辑补齐审批态恢复和阻塞态恢复：`resume` 只能恢复 `BLOCKED`，`approve` 只能推进 `WAITING_APPROVAL`，两者语义分开。  
验收标准：开启 `manual_approval` 后运行会在架构阶段暂停；审批通过后继续；`template_context` 能在生成的 brief、architecture 和 shared plan 中看到实际影响。

**公共接口与类型变更**
- `RunStatus` 新增 `WAITING_APPROVAL`。  
- `EventType` 新增 `CONTEXT_RESOLVED`、`PROMPT_BUILT`、`MODEL_CALL_STARTED`、`MODEL_CALL_FINISHED`、`ARTIFACT_INDEXED`、`APPROVAL_REQUIRED`、`APPROVAL_GRANTED`，并把现有 `NODE_LOG` 真正用起来。  
- `AgentTaskContext` 新增 `template_context`、`context_sources`、`shared_plan_id`。  
- 新增表：`run_checkpoints`、`shared_plans`、`context_documents`、`memory_summaries`、`prompt_traces`、`model_calls`、`approvals`。  
- 新增接口：`POST /runs/{id}/approve`、`GET /runs/{id}/trace`、`GET /runs/{id}/context-sources`。  
- 现有 `/runs`、`/runs/{id}`、`/runs/{id}/graph`、`/runs/{id}/resume`、`/runs/{id}/events/stream` 保持兼容，不改 URL。

**测试计划**
- 编排测试：验证 LangGraph 路径为 `PC -> CA -> FD/BD -> DE -> QT`，且 `QT FAIL` 会创建下一 cycle 并从 `CA` 重启。  
- 恢复测试：节点超时或 provider 异常后，`resume` 只重跑未完成节点，不重复执行已完成节点。  
- RAG 测试：手动知识、共享计划、产物、记忆都能被统一检索，并返回正确来源信息。  
- 记忆测试：完成一个 cycle 后会生成短记忆和摘要记忆，下一轮上下文组装顺序符合设计。  
- 审批测试：`manual_approval=true` 时 `CA` 后暂停，审批通过继续，审批拒绝进入阻塞。  
- 观测测试：SSE 能收到新增事件；前端能显示完整多 cycle DAG、节点详情和日志。  
- 回归测试：现有创建项目、启动 run、查看 graph、查看 artifacts 的接口行为不被破坏。

**假设与默认值**
- 保持现有技术栈不变：FastAPI、SQLAlchemy、Next.js、SQLite 默认开发，OpenAI-compatible provider 不变。  
- 继续采用单进程、单租户、本地课程项目部署模型，不在本轮加入鉴权、多人协作、分布式 worker。  
- `max_cycles` 继续上限 3，不在本轮扩展为任意轮。  
- 观测数据默认全部落库，课程项目版不做归档和清理策略。  
- 如果时间不足，唯一允许压缩的是 `v0.4` 前端交互细节；`v0.2` 和 `v0.3` 不能删，因为它们直接决定“项目描述是否真实成立”。
