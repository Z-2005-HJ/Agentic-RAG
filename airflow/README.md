# Airflow Configuration

> **中文说明：** 本文档为 **英中对照**：**保留英文原文**，在主要节后附 **中文** 释义。This README is **English–Chinese bilingual**: **English is preserved**, with **Chinese** notes added after major sections.

This directory contains Apache Airflow configuration and DAGs for the arXiv Paper Curator project.

> **中文：** 本目录存放 **Apache Airflow** 的配置与 **DAG**，用于 arXiv 论文策展项目的工作流编排。

<p align="center">
  <img src="../static/week2_data_ingestion_flow.png" alt="Week 2 Data Ingestion Architecture" width="800">
</p>

## Current Setup (Week 2)

> **中文 · 当前范围（第 2 周）：** 下列 DAG 与流水线能力对应课程第 2 周数据摄入阶段。

### Production-Ready DAGs
- **hello_world_dag.py**: Basic health check DAG for Week 1
- **arxiv_paper_ingestion.py**: Main production DAG for automated arXiv paper fetching and processing

### Production Pipeline Features
- **Daily arXiv ingestion**: Automated fetching of CS.AI papers
- **PDF processing**: Download and parse papers using Docling
- **Database storage**: Store complete paper metadata and content in PostgreSQL
- **Error handling**: Comprehensive retry logic and error reporting
- **Cross-platform compatibility**: Works on macOS, Linux, WSL, and Ubuntu

> **中文 · 流水线能力：** 每日拉取 arXiv、Docling 解析 PDF、元数据与正文入库 PostgreSQL、重试与错误报告、跨平台运行。

## Directory Structure

```
airflow/
├── README.md                           # This file
├── Dockerfile                          # Custom Airflow container with dependencies
├── requirements-airflow.txt            # Python dependencies for DAGs
└── dags/
    ├── hello_world_dag.py             # Week 1 health check DAG
    ├── arxiv_paper_ingestion.py       # Week 2 production ingestion DAG
    └── arxiv_ingestion/
        └── tasks.py                   # Production pipeline tasks with async processing
```

> **中文 · 目录：** `Dockerfile` 构建自定义 Airflow 镜像；`requirements-airflow.txt` 为 DAG 运行时依赖；`dags/` 下为具体 DAG 与任务模块（若与仓库实际文件名不一致，以目录为准）。

## Docker Configuration

### Cross-Platform Compatibility
The Airflow container is configured for cross-platform deployment:
- **User Configuration**: Runs as `airflow` user (50000:0) to avoid permission issues
- **Volume Management**: Uses named volumes for logs to prevent bind mount conflicts
- **Database Integration**: Connects to shared PostgreSQL instance
- **Service Dependencies**: Automatic initialization and health checks

### Container Features
- **Python 3.12** with Apache Airflow 2.10.3
- **PostgreSQL support** via psycopg2
- **PDF processing** with Docling, Tesseract OCR, and Poppler utilities
- **Rate limiting** and retry logic for arXiv API compliance
- **Async processing** for optimal performance with concurrent downloads and parsing

> **中文 · 容器特性：** Python 3.12 + Airflow、psycopg2、Docling/OCR/Poppler、arXiv 限流与异步并发。

## Usage

### Web Interface
- **URL**: http://localhost:8080
- **Credentials**: Auto-generated during container initialization
- **Features**: DAG monitoring, task logs, pipeline statistics

### Production DAG (`arxiv_paper_ingestion`)
1. **Environment Setup**: Verify services and initialize caching
2. **Daily Paper Fetch**: Retrieve papers from previous day (10 papers default)
3. **PDF Processing**: Download and parse PDFs with Docling
4. **Failed PDF Retry**: Handle any processing failures
5. **Database Storage**: Store complete paper data with parsed content
6. **OpenSearch Placeholders**: Prepare for Week 3+ search indexing
7. **Daily Report**: Generate comprehensive processing statistics

> **中文 · 生产 DAG 步骤概览：** 环境检查 → 按日拉取论文 → PDF 下载与解析 → 失败重试 → 入库 → 为后续 OpenSearch 预留占位 → 日报统计。

### Pipeline Performance
- **Concurrent Processing**: 5 parallel downloads, 1 parsing operation (laptop-optimized)
- **Rate Limiting**: Respects arXiv API guidelines (3-second delays)
- **Caching**: PDF files cached locally to avoid re-downloading
- **Error Resilience**: Continues processing even with individual paper failures

> **中文 · 性能：** 并行下载/解析、遵守 arXiv 间隔、本地 PDF 缓存、单篇失败不阻断整批。

## Configuration

### Environment Variables
```bash
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://rag_user:rag_password@postgres:5432/rag_db
AIRFLOW__CORE__EXECUTOR=LocalExecutor
POSTGRES_DATABASE_URL=postgresql+psycopg2://rag_user:rag_password@postgres:5432/rag_db
PYTHONPATH=/opt/airflow/src
```

### Service Dependencies
- **PostgreSQL**: Paper metadata and content storage
- **Source Code**: Mounted from `../src` for service access
- **Shared Network**: Communication with API and database services

> **中文 · 依赖：** 与共享 PostgreSQL、挂载的 `src`、Compose 网络互通。

## Week 2 Implementation Status

### ✅ Completed Features
- Custom Docker container with all dependencies
- Production arXiv ingestion DAG with comprehensive error handling
- Async PDF processing pipeline with concurrency control
- PostgreSQL integration with complete content storage
- Cross-platform compatibility (macOS, Linux, WSL, Ubuntu)
- Rate limiting and retry logic for arXiv API compliance
- Detailed logging and monitoring throughout pipeline

> **中文 · 已完成：** 自定义镜像、生产级 DAG、异步 PDF 流水线、PostgreSQL 全量存储、跨平台、限流重试、日志监控。

### 🔄 Week 3+ Roadmap
- **OpenSearch Integration**: Real search indexing (currently placeholders)
- **Advanced Scheduling**: Multiple collection strategies
- **Monitoring & Alerting**: Production observability
- **Scale Optimization**: Higher concurrency for production workloads

> **中文 · 后续路线：** 真正接入 OpenSearch 索引（文中占位）、更多调度策略、监控告警、提高并发以贴近生产负载。