# Job Copilot

基于真实上市公司招聘数据的求职助手 Agent：语义岗位检索、简历匹配、职业规划与面试准备，支持多 Agent 编排、MCP 工具接入、会话记忆与流式对话。

## 功能

| 功能 | 说明 |
| --- | --- |
| 语义岗位检索 | 自然语言查询 → 意图理解 → Milvus 向量召回 → Reranker 重排 → LLM Judge 与查询改写重试 |
| 简历匹配 | 简历与岗位要求逐项对比，输出匹配度与改进建议 |
| 职业规划 / 面试准备 | 主 Agent 委派给岗位、简历、职业、面试四个子 Agent |
| 多 Agent 编排 | LangGraph + DeepAgents，SQLite Checkpoint 支持多轮连续与中断恢复 |
| MCP | 本地工具（岗位检索、Tavily 联网搜索）+ 外部 MCP 服务动态发现与统一注册 |
| 记忆 | Mem0 长期记忆 + 会话历史 + 上下文压缩，Redis 缓存与运行锁 |
| 前端 | Vue 3 聊天界面，SSE 流式输出与工具调用记录展示 |

## 架构

```text
Vue 前端 (5173) ─┐
FastAPI 后端 (8001) ─┼─ 多 Agent (LangGraph + DeepAgents)
MCP 客户端      ─┘       ├─ Milvus 向量库 (岗位 / 记忆)
                         ├─ Redis (缓存 / 会话锁)
                         ├─ SQLite Checkpoint + Mem0 (历史 / 长期记忆)
                         └─ LLM: SERVICE_LLM(检索与简历) + AGENT_LLM(主 Agent)
```

## 快速开始

### 1. 环境

- Python 3.11（推荐 conda 环境，依赖安装见下）
- Docker（Milvus / Redis 基础设施）
- Node.js 18+（前端）

```powershell
pip install -r requirements.txt
```

### 2. 配置

```powershell
Copy-Item .env.example .env   # 然后填写 API Key
```

必填项：

- `SERVICE_LLM_API_KEY` / `SERVICE_LLM_BASE_URL` / `SERVICE_LLM_MODEL`：检索、简历等服务的 LLM（默认 DeepSeek）
- `AGENT_LLM_API_KEY` / `AGENT_LLM_BASE_URL` / `AGENT_LLM_MODEL`：主 Agent 的 LLM（默认 MiniMax）
- `EMBEDDING_MODEL` / `RERANKER_MODEL`：本地模型路径，默认 `localmodel/bge-small-zh-v1.5` 与 `localmodel/BAAI-bge-reranker-v2-m3`（模型文件不入库，需自行下载）
- 可选：`TAVILY_API_KEY`（联网搜索）、`REDIS_ENABLED`、`MEMORY_ENABLED` 等

### 3. 基础设施与数据

```powershell
# 启动 Milvus + Redis（含 etcd/minio）
docker compose -f infra/docker-compose.yml up -d redis etcd minio milvus

# 建 collection 并导入岗位数据（数据文件 data/*.csv 不入库，需自行准备）
python scripts/create_collection.py
python scripts/ingest_jobs.py --file data/上市公司招聘数据2026.csv --limit 1000
```

### 4. 启动

一键启动（Redis + 后端 8001 + MCP 8000 + 前端 5173）：

```powershell
.\scripts\start-dev.ps1
```

或分别启动：

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload   # 后端
python -m app.mcp.server                                              # MCP 服务
cd vue; npm install; npm run dev                                      # 前端
```

### 5. 验证

```powershell
# 测试（务必用项目 conda 环境的 python，全局 python 缺少依赖）
python -m pytest -q

# 一条真实检索（服务层全链路：意图理解 → embedding → Milvus → rerank → judge）
python runtime/smoke_query.py

# HTTP 接口示例
# GET http://127.0.0.1:8001/jobs/search?query=数据分析师%20SQL%20Python&city=北京&top_k=5
# GET http://127.0.0.1:8001/health
```

## 目录结构

```text
app/            FastAPI 后端：agents(LangGraph) / api / mcp / rag / services / schemas / prompts / security
vue/            前端 Vue 3
scripts/        建库、数据导入、启动脚本
infra/          Docker Compose（Milvus、Redis、后端、MCP、前端）
tests/          组件与接口测试（pytest，12 个用例）
docs/           部署等说明
runtime/        运行期数据（Milvus、Redis 持久化目录，不入库）
outputs/        运行产物（Checkpoint、Mem0、评测输出，不入库）
```

## 已知限制

- 检索按语义相似度排序，**不校验**用户硬条件（城市、应届、外包等），可能返回不符合条件的岗位；改进中
- 历史招聘数据未做时效核验，不能视为当前可投递岗位
- 简历匹配分数主要由 LLM 给出，缺少可复现的证据依据
- 引用来源目前从回答文本提取，尚未形成结构化证据链
- 会话接口未绑定用户身份认证

## 相关文档

- 部署：[docs/deployment.md](docs/deployment.md)
- 改进路线与阶段计划：`plan/Improvement.md`、`plan/Phase1-Retrieval-Plan.md`
