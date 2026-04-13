"""Patch notebooks/week1/week1_setup.ipynb with richer English+Chinese markdown and code comment hints.

Run from repo root: uv run python scripts/patch_week1_notebook_bilingual.py
"""

from __future__ import annotations

import json
from pathlib import Path


def cell_md(text: str) -> list[str]:
    """Notebook source as list of lines (Jupyter-friendly)."""
    if not text.endswith("\n"):
        text += "\n"
    return [text]


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    path = root / "notebooks" / "week1" / "week1_setup.ipynb"
    nb = json.loads(path.read_text(encoding="utf-8"))
    cells = nb["cells"]

    # Markdown cells by index (verified against week1_setup.ipynb structure)
    md_blocks: dict[int, str] = {
        0: """# 中文导读 / Chinese Guide（Week 1）

**说明 / Note：** 下方单元格**保留原始英文**（标题、说明、输出与代码内字符串）；本格用中文概括第 1 周任务。
**Note:** Cells below **keep the original English**; this cell summarizes Week 1 in Chinese.

- **本周你要完成：** 用 Docker Compose 启动全套服务 → 逐个做健康检查 →（可选）拉取小模型验证 Ollama。
- **端口速记：** FastAPI **8000** · PostgreSQL **5432** · OpenSearch **9200** / Dashboards **5601** · Airflow **8080** · Ollama **11434**。
- **更细的逐段说明：** 见同目录 `README.md`（已做英中对照）。

---
""",
        1: """# arXiv Paper Curator - Week 1: Infrastructure Setup

Build a production-grade RAG system using Docker, PostgreSQL, OpenSearch, FastAPI, Airflow, and Ollama.

> **中文：** 本周目标是用 Docker 把 **API、数据库、搜索引擎、工作流编排、本地 LLM** 跑在同一套 Compose 栈里，为后续 RAG 打地基。

## Technology Stack
| Component | Purpose | Port |
|-----------|---------|------|
| **FastAPI** | REST API | 8000 |
| **PostgreSQL** | Paper metadata storage | 5432 |
| **OpenSearch** | Hybrid search engine | 9200/5601 |
| **Apache Airflow** | Workflow automation | 8080 |
| **Ollama** | Local LLM inference | 11434 |

> **中文 · 表格对照：** **FastAPI** 对外 HTTP；**PostgreSQL** 存论文表；**OpenSearch** 提供检索与仪表板；**Airflow** 跑 DAG；**Ollama** 在本地跑模型（后续周会深度使用）。

---
""",
        2: """## Learning Materials

**Core Technologies:**
- **Docker**: [Tutorial Video](https://www.youtube.com/watch?v=pg19Z8LL06w) | [Docker Compose](https://www.youtube.com/watch?v=SXwC9fSwct8)
- **FastAPI**: [YouTube Series](https://www.youtube.com/playlist?list=PLK8U0kF0E_D6l19LhOGWhVZ3sQ6ujJKq_) | [Documentation](https://fastapi.tiangolo.com/tutorial/)
- **PostgreSQL**: [Beginners Guide](https://www.youtube.com/watch?v=SpfIwlAYaKk) | [FastAPI + PostgreSQL](https://www.youtube.com/watch?v=398DuQbQJq0)
- **OpenSearch**: [Getting Started](https://docs.opensearch.org/latest/getting-started/)
- **Apache Airflow**: [Tutorial Video](https://www.youtube.com/watch?v=Y_vQyMljDsE)

**Development Tools:**
- **VS Code Setup**: [Video Guide](https://www.youtube.com/watch?v=mpk4Q5feWaw)
- **Git Basics**: [Tutorial](https://www.youtube.com/watch?v=zTjRZNkhiEU)
- **UV Package Manager**: [Setup Video](https://www.youtube.com/watch?v=AMdG7IjgSPM)

> **中文：** 以上为 **拓展视频与官方文档**（英文为主）。遇到概念卡点时，可点开对应链接；不必一次看完，按当周进度查阅即可。

---
""",
        3: """## Prerequisites

**Required Software:**
- Python 3.12+ ([Download](https://www.python.org/downloads/))
- UV Package Manager ([Install Guide](https://docs.astral.sh/uv/getting-started/installation/))
- Docker Desktop ([Download](https://docs.docker.com/get-docker/))
- Git ([Download](https://git-scm.com/downloads))

**System Requirements:**
- 8GB+ RAM (16GB recommended)
- 20GB+ free disk space

> **中文 · 环境清单：** 需要 **Python 3.12+**、**UV**、**Docker Desktop**（含 Compose）、**Git**；内存建议 **≥8GB（16GB 更舒服）**，磁盘预留 **≥20GB** 给镜像与模型。

---
""",
        4: """## Setup Instructions

**Before running cells:**
1. Extract/clone project to your system
2. Open terminal in project root (contains `compose.yml`)
3. Run: `uv sync`
4. Start Jupyter: `uv run jupyter notebook`
5. Verify kernel shows project environment (.venv)

> **中文 · 运行前准备：**  
> 1) 克隆/解压到本机；2) 终端 **cd 到项目根目录**（能看到 `compose.yml`）；3) `uv sync` 安装依赖；4) 启动 Jupyter；5) 内核选 **.venv**，确保 `requests` 等与项目一致。

---
""",
        10: """## Start Services

**Command to run (in terminal):**
```bash
cd [project-root]
docker compose up -d
```

**What this does:** Downloads images (first time) and starts all services in background.

> **中文：** 在终端于项目根执行 `docker compose up -d`：**首次**会拉取镜像较慢；`-d` 表示后台运行。若你使用 `docker compose up --build -d` 亦可（会重建镜像，耗时更长）。

---
""",
        13: """## Service Health Verification

All services start automatically. Check their health status:

> **中文：** 容器启动后 **1–5 分钟**内处于 `starting` / `health: starting` 是正常的；OpenSearch、Airflow 往往最慢。可多次重跑下方检查单元格。

---
""",
        16: """### 1. FastAPI - REST API Service

**Interactive Exploration:**

You can explore and test the FastAPI service in several ways:
- **API Documentation**: http://localhost:8000/docs (Interactive Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc interface)
- **Source Code**: Located in `src/routers/` directory

Let's test the API endpoints and explore the documentation:

> **中文：** 浏览器打开 **/docs** 可交互试接口；**ReDoc** 适合阅读文档样式；实现代码在 `src/routers/`。健康检查常用 **`GET /api/v1/health`**。

---
""",
        19: """### 2. Apache Airflow - Workflow Automation

**Interactive Exploration:**

Apache Airflow manages data pipelines and automated workflows. You can explore it through:
- **Web Dashboard**: http://localhost:8080 
- **Login**: Username: `admin`, Password: Found in container (see test below)
- **Source Code**: Located in `airflow/dags/` directory

**Simple Password Location:**
Airflow 3.0 stores the admin password in a predictable file:
```
/opt/airflow/simple_auth_manager_passwords.json.generated
```

The test below automatically reads this file for you!

Let's test Airflow and get the password:

> **中文：** Airflow Web **8080**；默认用户 **admin**，密码在宿主机挂载生成的 **`airflow/simple_auth_manager_passwords.json.generated`**（下方代码会尝试读取）。DAG 代码在 `airflow/dags/`。

---
""",
        22: """### 3. OpenSearch - Hybrid database

**Interactive Exploration:**

OpenSearch provides full-text search and analytics capabilities:
- **API Endpoint**: http://localhost:9200 
- **Dashboards UI**: http://localhost:5601 (Web interface)
- **Source Code**: Located in `src/services/opensearch/` directory

**Important for Students:** 
- ✅ Use http://localhost:5601 for web interface
- ✅ Use Dev Tools in Dashboards for API queries

Let's test OpenSearch and explore its capabilities:

> **中文：** **5601** 是 OpenSearch Dashboards（推荐从这里探索）；**9200** 是 HTTP API。学生练习可在 Dashboards 的 **Dev Tools** 里发 `GET /_cluster/health` 等请求。客户端封装见 `src/services/opensearch/`。

---
""",
        25: """### 4. Ollama - Local LLM Inference Engine

**Interactive Exploration:**

Ollama runs large language models locally on your machine:
- **API Endpoint**: http://localhost:11434
- **Command Line**: Available inside the container
- **Privacy**: All AI processing happens locally (no external APIs)

Let's test Ollama and see what models are available:

> **中文：** Ollama 在 **本机/容器内** 提供兼容 OpenAI 风格的 HTTP API（`/api/tags`、`/api/generate` 等）。**第 1 周**只需确认服务可用；**拉模型**可在后文动手单元或第 4 周再做。

---
""",
        31: """### 5. PostgreSQL - Database Storage

**Interactive Exploration:**

PostgreSQL stores all structured data for our application:
- **Connection**: localhost:5432
- **Database**: rag_db
- **Username/Password**: rag_user / rag_password
- **GUI Tool Recommendation**: DBeaver (free database client)

Let's test the database connection and explore the schema:

> **中文：** 默认连接 **localhost:5432**，库 **`rag_db`**，用户 **`rag_user` / `rag_password`**（与 `compose.yml` 一致，仅供本地学习）。可用 **DBeaver** 或 **pgAdmin** 图形化查看表结构。

---
""",
        36: """### Service Health Summary and Next Steps

Based on the interactive tests above:

**If all services show ✓**: 
- 🎉 Congratulations! Your infrastructure is ready
- All services are healthy and responding correctly
- You can explore each service using the links and instructions provided

**If some services show ✗**:
- Don't worry! Services take time to start
- Wait 2-3 minutes and re-run the test cells
- OpenSearch and Airflow take the longest (up to 5 minutes)

**Service Access Points:**
- **FastAPI Documentation**: http://localhost:8000/docs - Interactive API testing
- **Airflow Dashboard**: http://localhost:8080 (username `admin`; password in `airflow/simple_auth_manager_passwords.json.generated`) - Workflow management
- **OpenSearch Dashboards**: http://localhost:5601 - Dashboard and user interface + analytics
- **OpenSearch API**: http://localhost:9200 - Direct API access
- **Ollama API**: http://localhost:11434 - Local LLM inference
- **PostgreSQL**: http://localhost:5432 - Use DBeaver or similar tools

**Hands-On Learning Activities:**

1. **FastAPI**: Test endpoints in the interactive documentation
2. **Airflow**: Login and trigger a DAG manually  
3. **OpenSearch**: Try queries in the Dev Tools
4. **Ollama**: Prepare for Week 6 model installation
5. **PostgreSQL**: Install DBeaver and explore the database structure

**Common Issues:**
- "Connection refused" → Service still starting
- "Port in use" → Another application using the port  
- Container restarting → Check logs with `docker compose logs [service-name]`

> **中文 · 小结：** 若多为 ✓，说明基础设施就绪；若有 ✗，先 **等待并重跑**，再看 **`docker compose logs <服务名>`**。上表 URL 为默认本机地址；Airflow 密码以你机器上生成的文件为准（勿照抄笔记里示例密码）。**动手建议**与英文列表一致：玩 `/docs`、手动触发 DAG、Dev Tools 查集群、（可选）装 GUI 看库表。

---
""",
        37: """## Troubleshooting

**Common Issues:**
- **Connection refused** → Service still starting (wait 2-3 minutes)
- **Port in use** → Stop conflicting application or change ports
- **Container restarting** → Check logs: `docker compose logs [service-name]`
- **Out of memory** → Increase Docker Desktop memory allocation

**Reset everything:** `docker compose down && docker compose up -d`

> **中文 · 排错：** **拒绝连接** 多半是还没起完；**端口占用** 先停冲突程序或改映射；**容器反复重启** 必看日志；**内存不足** 调高 Docker Desktop 分配。需要彻底重来可用 `docker compose down && docker compose up -d`（注意是否会丢未持久化数据）。

---
""",
        38: """## Week 1 Complete

**Service Access Points:**
- **API**: http://localhost:8000/docs
- **Airflow**: http://localhost:8080 (username: `admin`; password: see `airflow/simple_auth_manager_passwords.json.generated`)  
- **OpenSearch**: http://localhost:5601
- **PostgreSQL**: localhost:5432 (rag_user/rag_password)

**Success Criteria:**
- [ ] All services healthy in status check
- [ ] API documentation accessible
- [ ] Airflow dashboard loads
- [ ] OpenSearch interface works

**Next:** Keep services running or restart with `docker compose up -d`

> **中文 · 完成标准与注意：** 勾选项与英文相同。Airflow 密码**每次生成**，请读你本机 **`airflow/simple_auth_manager_passwords.json.generated`**，勿使用他人机器上的值。完成后可保持 `docker compose up -d` 常开，进入第 2 周。

---
""",
        39: """## Project Commands

**Makefile shortcuts:**
```bash
make start    # Start all services  
make status   # Check service status
make logs     # View logs
make health   # Check service health
make stop     # Stop all services
make help     # View all commands
```

**Next:** Read the main `README.md` for complete project documentation.

> **中文：** `make help` 可查看全部快捷命令；与手动 `docker compose` 等价封装。更完整的项目说明见仓库根目录 **`README.md`**（已附中文对照块）。

---
""",
    }

    for idx, text in md_blocks.items():
        if cells[idx].get("cell_type") != "markdown":
            raise SystemExit(f"Cell {idx} is not markdown")
        cells[idx]["source"] = cell_md(text)

    # Code cells: append Chinese hint to first-line comment where applicable
    code_comment_prefix: dict[int, str] = {
        5: "# Environment Check  # 检查 Python 版本是否为 3.12+ 并打印解释器路径\n",
        6: "# Find Project Root  # 定位项目根目录（含 compose.yml）\n",
        7: "# Check Docker  # 检查 docker CLI 是否可用\n",
        8: "# Check Docker Compose  # 检查 docker compose 子命令\n",
        9: "# Check UV Package Manager  # 检查 uv 是否安装\n",
        11: "# Check Docker Running  # 确认 Docker 守护进程已运行\n",
        12: "# Check Current Containers  # 列出 compose 栈内容器状态\n",
        14: "# Service Health Check  # 汇总期望服务与实际运行/健康状态\n",
        15: "# Check Missing Services  # 提示缺失或失败服务及日志命令\n",
        17: "# Test FastAPI Health  # 请求 API 健康检查端点\n",
        18: "# PRODUCTION INSIGHTS  # 生产向思考题（课程延伸）\n",
        20: "# Get Airflow Password  # 从生成的 JSON 读取 admin 密码\n",
        21: "# Test Airflow Health  # 请求 Airflow 健康 API 并打印登录信息\n",
        23: "# Test 1: Check OpenSearch Dashboards Web Interface  # 验证 5601 仪表板可访问\n",
        24: "# PRODUCTION DEPLOYMENT INSIGHT  # OpenSearch 生产向思考题\n",
        26: "# Test 1: Check Ollama Service Status  # 查看已安装模型列表\n",
        27: "# Test 2: Check Ollama Version and Health  # 查看 Ollama 版本与说明文字\n",
        28: "# PRODUCTION DEPLOYMENT INSIGHT  # LLM 生产向思考题\n",
        29: "# HANDS-ON: Pull and Test Llama 3.2 (Small Model)  # 可选：在容器内拉取小模型\n",
        30: "# Test Llama 3.2:1b API  # 可选：调用 /api/generate 做一次生成测试\n",
        32: "# Test 1: Check PostgreSQL Connection (Basic)  # 用端口探测检查 5432 是否可达\n",
        33: "# Test PostgreSQL Connection  # 使用 psycopg2 尝试真实连接\n",
        34: "# Check Database Tables  # 列出 public schema 表（含 Airflow 元数据表）\n",
        35: "# PRODUCTION DEPLOYMENT INSIGHT  # PostgreSQL 生产向思考题\n",
    }

    for idx, first_line in code_comment_prefix.items():
        if cells[idx].get("cell_type") != "code":
            raise SystemExit(f"Cell {idx} is not code")
        src = cells[idx]["source"]
        if not src:
            continue
        # Replace first line if it starts with #
        if isinstance(src, str):
            lines = src.splitlines(keepends=True)
        else:
            lines = src
        if not lines:
            continue
        if lines[0].lstrip().startswith("#"):
            lines[0] = first_line
        else:
            lines.insert(0, first_line)
        cells[idx]["source"] = lines

    path.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("Patched", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
