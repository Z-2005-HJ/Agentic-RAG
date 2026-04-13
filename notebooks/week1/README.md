# Week 1: Infrastructure Setup and Verification

> **中文说明：** 本页为 **英中对照**：**保留全部英文原文**，在段后或表后附 **中文** 释义，便于完成第 1 周任务时对照阅读。

This folder contains the materials for Week 1 of the arXiv Paper Curator project, which focuses on setting up and verifying the complete infrastructure stack.

> **中文：** 本文件夹包含 **第 1 周** 学习材料：搭建并 **验证** 完整基础设施栈（容器、数据库、搜索引擎、API、编排与本地 LLM 等）。

## Contents

### `week1_setup.ipynb`

A comprehensive Jupyter notebook that guides students through:

> **中文：** `week1_setup.ipynb` 会带你 **逐步** 完成环境与服务的检查（建议从上到下依次运行单元格）。

1. **System Requirements and Setup**
   - Understanding each technology component and its purpose
   - Cross-platform installation instructions (Windows, macOS, Linux)
   - Prerequisites verification with automated checking

> **中文 · 系统与安装：** 弄清每个组件 **做什么**；按 Windows / macOS / Linux 安装依赖；用 notebook 里的检查单元格 **自动验证** 版本与工具是否就绪。

2. **Infrastructure Architecture**
   - Complete overview of the multi-service architecture
   - Understanding how Docker containers communicate
   - Data persistence and volume management concepts

> **中文 · 架构：** 多服务如何组成一套系统；容器之间如何在 **Docker 网络** 里通信；**数据卷** 如何持久化数据。

<p align="center">
  <img src="../../static/week1_infra_setup.png" alt="Week 1 Infrastructure Setup" width="700">
</p>

**Architecture Overview:**
- **FastAPI** (Port 8000): REST API with async support and automatic documentation
- **PostgreSQL 16** (Port 5432): Primary database for paper metadata and content storage
- **OpenSearch 2.19** (Ports 9200, 5601): Hybrid search engine with management dashboards
- **Apache Airflow 3.0** (Port 8080): Workflow orchestration with DAGs and PostgreSQL backend
- **Ollama** (Port 11434): Local LLM server for future RAG implementation
- **Docker Network**: All services communicate via `rag-network` with persistent volumes

> **中文 · 组件与端口一览：**  
> - **FastAPI 8000**：异步 REST API，自带 `/docs` 文档。  
> - **PostgreSQL 5432**：论文元数据与内容的关系型存储。  
> - **OpenSearch 9200 / Dashboards 5601**：检索引擎与可视化界面。  
> - **Airflow 8080**：DAG 工作流编排（后台常用 Postgres）。  
> - **Ollama 11434**：本地大模型推理服务（后续 RAG 会用到）。  
> - **`rag-network` + volumes**：服务互通与数据持久化。

3. **Service-by-Service Setup**
   - PostgreSQL database for paper metadata storage
   - OpenSearch for full-text search capabilities
   - Apache Airflow for workflow automation
   - Ollama for local LLM inference
   - FastAPI for REST API endpoints

> **中文 · 分服务理解：** 各服务 **职责单一**：Postgres 存数据，OpenSearch 做检索，Airflow 跑定时任务，Ollama 跑模型，FastAPI 对外提供 HTTP 接口。

4. **Verification and Testing**
   - Automated health checks for all services
   - Step-by-step verification procedures
   - Modular Ollama testing (4 focused test cells)
   - Common troubleshooting scenarios and solutions

> **中文 · 验证：** notebook 会带你做 **健康检查**、按步骤确认每个服务；Ollama 部分拆成多个小实验；文末有 **排错** 提示。

## Learning Objectives

By completing this week's materials, students will:

- Understand containerization and Docker Compose orchestration
- Learn how to set up a production-grade infrastructure stack
- Gain experience with database design and API development
- Master troubleshooting techniques for multi-service applications
- Learn direct HTTP API testing vs service abstraction layers
- Build confidence working with professional development tools

> **中文 · 学习目标：**  
> - 理解 **容器化** 与 **Compose 编排** 的基本用法。  
> - 能独立拉起一套接近 **生产形态** 的多服务栈。  
> - 熟悉 **数据库连接** 与 **API 文档驱动** 的调试方式。  
> - 掌握多服务场景下的 **日志 / 端口 / 健康检查** 排错思路。  
> - 区分「直接用 HTTP 测服务」与「在代码里封装客户端」的差异。  
> - 建立使用 UV、Docker、Jupyter 等 **工程化工具** 的信心。

## Ollama Testing (Simplified for Week 1)

The notebook includes modular Ollama testing broken into focused cells:

> **中文：** 第 1 周对 Ollama **不做硬性要求**（无模型也能先做健康检查）；notebook 把实验拆成多个小步骤，便于你按需运行。

- **Test 3A**: Check available models
- **Test 3B**: Simple model testing (if models installed) 
- **Test 3C**: Performance analysis
- **Test 3D**: Learning notes and setup commands

> **中文 · 模块含义：**  
> - **3A**：查看已安装模型列表。  
> - **3B**：若已拉取模型，可做简单生成测试。  
> - **3C**：粗略观察响应耗时（视机器而定）。  
> - **3D**：补充说明与常用命令。

### Easy Model Installation (Optional for Week 1)

```bash
# Using Makefile (recommended)
make ollama-pull MODEL=llama3.2:1b
make ollama-test MODEL=llama3.2:1b

# Direct HTTP calls for learning
curl -X POST http://localhost:11434/api/pull -d '{"name":"llama3.2:1b"}'
curl -X POST http://localhost:11434/api/generate -d '{"model":"llama3.2:1b","prompt":"Hello","stream":false}'
```

> **中文 · 命令说明：**  
> - `make ollama-pull ...`：用 Makefile 快捷拉取模型（推荐）。  
> - `curl .../pull`：直接向 Ollama HTTP API 拉模型（便于理解原理）。  
> - `curl .../generate`：非流式生成一次文本（`stream:false`）。

### Recommended Models for Course

- **llama3.2:1b** (1.2GB) - Fast, good for testing
- **llama3.2:3b** (2.0GB) - Balance of speed/quality
- **llama3.1:8b** (4.7GB) - Better quality, slower

> **中文 · 模型建议：** **1b** 最小最快，适合验证通路；**3b** 平衡；**8b** 质量更好但更吃资源与时间。

**Note**: No models are required for Week 1 - service health check works without them.

> **中文：** **第 1 周不强制下载模型**；只要 Ollama **服务进程**正常，就算完成当周「推理引擎就位」的检查目标。

## Target Audience

This material is designed for:
- **Beginners** who want to learn modern software infrastructure
- **Students** looking to understand how real-world applications are built
- **Professionals** transitioning into software development or DevOps
- **Anyone** interested in building their own AI-powered research tools

> **中文 · 适合人群：** 想入门现代基础设施的 **初学者**；希望了解真实应用如何落地的 **学生**；转向开发或 DevOps 的 **从业者**；以及想自建 **AI 研究工具** 的任何人。

## Time Commitment

- **Setup**: 2-3 hours (including software installation and downloads)
- **Notebook completion**: 1 hours
- **Total**: 2-4 hours

> **中文 · 时间预估：** 首次安装 Docker / 拉镜像可能 **2–3 小时**；完整跑通 notebook 约 **1 小时**；合计大约 **2–4 小时**（因网络与机器性能差异会浮动）。

## 📖 Additional Resources

**Week 1 Blog Post:** [The Infrastructure That Powers RAG Systems](https://jamwithai.substack.com/p/the-infrastructure-that-powers-rag)
- Deep dive into each infrastructure component
- Production deployment considerations
- Architecture decision explanations

> **中文 · 延伸阅读：** 博客会对每个组件做更深讲解，并涉及 **生产部署** 与 **架构取舍**（建议读完 notebook 后再读）。

## Support Resources

If you encounter issues:
1. Check the troubleshooting sections in the notebook
2. Review the common problems and solutions
3. Ensure all prerequisites are properly installed
4. Follow the step-by-step verification procedures
5. Ask in Jam With AI substack chat channel

> **中文 · 遇到问题：**  
> 1) 先看 notebook 的 **Troubleshooting**；  
> 2) 对照「常见问题」逐项排除；  
> 3) 确认 Python / UV / Docker / Git 版本满足要求；  
> 4) 严格按验证步骤重试；  
> 5) 可在课程社区 / Substack 频道提问。

## Next Steps

After completing Week 1, you will be ready to:
- Understand how each service contributes to the overall system
- Modify and extend the infrastructure as needed
- Proceed to Week 2: arXiv Integration and PDF Processing
- Build confidence in working with professional development environments

> **中文 · 下一步：** 理解各服务在整体中的角色后，可进入 **第 2 周：arXiv 集成与 PDF 处理**；届时你会把「基础设施」真正接到「数据入口」上。
