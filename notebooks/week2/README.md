# Week 2: arXiv API Integration & PDF Processing

> **中文说明：** 本页为 **英中对照**：**保留全部英文原文**，在主要章节或段落后增加 **中文** 释义，便于完成第 2 周任务时对照阅读。

This folder contains the materials for Week 2 of the arXiv Paper Curator project, which focuses on building the core data ingestion pipeline that feeds fresh academic content into our RAG system.

> **中文：** 本文件夹包含 **第 2 周** 学习材料：搭建 **数据摄入流水线**——从 arXiv 拉取论文、下载与缓存 PDF、用 **Docling** 解析、将元数据与内容写入 **PostgreSQL**，并对接 **Airflow** 为后续自动化做准备。

## Contents

### `week2_arxiv_integration.ipynb`

A comprehensive Jupyter notebook that guides students through:

> **中文：** `week2_arxiv_integration.ipynb` 会带你 **按顺序** 验证 Week 1 服务、调用 arXiv 客户端、测 PDF 下载与解析、测数据库写入与完整流水线；建议 **从上到下** 依次运行单元格。

1. **Infrastructure Validation**
   - Verify all Week 1 services are running correctly
   - Container health checks and fresh build verification
   - Environment setup for Week 2 components

> **中文 · 环境与验证：** 确认 Docker 栈已启动；必要时按文中说明 **重建镜像/清卷** 以匹配 Week 2 的数据库 schema；再跑 notebook 里的健康检查单元格。

2. **arXiv API Integration**
   - Building a robust client with rate limiting and retry logic
   - Implementing date-based filtering for targeted paper retrieval
   - Testing CS.AI category searches with proper API etiquette

> **中文 · arXiv：** 学习 **限流与重试**（避免被封或 503）；用 **日期区间** 缩小检索；理解客户端如何映射到项目中的 `ArxivClient` / `make_arxiv_client`。

<p align="center">
  <img src="../../static/week2_data_ingestion_flow.png" alt="Week 2 Data Ingestion Architecture" width="800">
</p>

**Data Pipeline Overview:**
- **MetadataFetcher**: 🎯 Main orchestrator coordinating the entire pipeline
- **ArxivClient**: Rate-limited fetching with retry logic (3-second delays)
- **PDFParserService**: Scientific PDF parsing with structured content extraction
- **PaperRepository**: PostgreSQL integration with upsert operations
- **Airflow DAGs**: Automated daily ingestion workflows

> **中文 · 流水线角色：**  
> - **MetadataFetcher**：编排「拉取 → 下载 → 解析 → 入库」的主流程。  
> - **ArxivClient**：带 **约 3 秒间隔** 等策略的请求封装。  
> - **PDFParserService（Docling）**：把 PDF 转为结构化/文本内容。  
> - **PaperRepository**：对 Postgres 做 **upsert**，避免重复主键。  
> - **Airflow DAGs**：定时触发同一套逻辑（本 notebook 也会检查 DAG 是否注册）。

3. **PDF Processing Pipeline**
   - Download and cache PDF files with proper error handling
   - Parse scientific PDFs using Docling for structured content extraction
   - Handle parsing failures gracefully with fallback mechanisms

> **中文 · PDF：** 下载到本地缓存目录；**并非所有 PDF** 都能被 Docling 完美解析，失败时应 **记录并继续** 后续论文，这是生产中的常态。

4. **Database Integration**
   - Store paper metadata and content in PostgreSQL
   - Implement upsert logic to avoid duplicates
   - Test retrieval and query operations

> **中文 · 数据库：** 元数据与（可选）解析结果写入 `rag_db`；**upsert** 保证同一 arXiv ID 重复跑不会炸；notebook 会测写入与按 ID 读回。

5. **Complete Pipeline Testing**
   - End-to-end processing from arXiv API to database storage
   - Error handling and graceful degradation testing
   - Performance metrics and success rate analysis

> **中文 · 端到端：** 用 `MetadataFetcher` 跑小批量，看统计字段（拉取数、下载数、解析数、入库数、错误列表）；理解 **部分失败不影响整体继续**。

6. **Production Readiness**
   - Airflow DAG status verification
   - Error logging and monitoring capabilities
   - Ready for automated daily ingestion

> **中文 · 自动化就绪：** 在容器内执行 `airflow dags list` 等检查 DAG 是否可见；导入错误常与 **镜像内依赖** 有关，按 notebook 提示排查。

## Learning Objectives

By completing this week's materials, students will:

- Master API integration with proper rate limiting and error handling
- Learn PDF processing techniques for scientific documents
- Understand database design patterns for research data storage
- Build robust data pipelines with comprehensive error handling
- Gain experience with async Python programming patterns
- Learn workflow automation concepts with Apache Airflow
- Develop skills in production-grade data processing systems

> **中文 · 学习目标：**  
> - 掌握 **外部 HTTP API** 的限流、重试与错误分类。  
> - 了解 **科学 PDF** 解析的常见坑与降级策略。  
> - 理解 **研究型数据** 在关系库中的建模与 **upsert** 模式。  
> - 建立 **异步（async/await）** 在 IO 密集流水线中的直觉。  
> - 知道 **Airflow** 如何把「脚本化流程」变成「可调度、可观测」的任务。  
> - 形成 **生产级数据管道**：可失败、可重跑、可监控。

## Key Technologies & Services

### Core Services (Built This Week)
- **arXiv API Client** - Fetches CS.AI papers with intelligent rate limiting
- **PDF Parser (Docling)** - Extracts structured content from scientific PDFs
- **Metadata Fetcher** - Orchestrates the complete processing pipeline
- **Database Repository** - Handles PostgreSQL operations with SQLAlchemy

> **中文 · 本周实现重点：** 客户端、解析器、编排器、仓储四层分工清晰，便于单测与替换实现。

### Infrastructure Dependencies (From Week 1)
- **PostgreSQL 16** - Paper metadata and content storage
- **FastAPI** - REST API endpoints for paper retrieval
- **Apache Airflow** - Workflow orchestration and scheduling
- **Docker Compose** - Service orchestration and networking

> **中文 · 依赖 Week 1：** 数据库与 API 容器必须健康；Compose 网络让服务用 **服务名** 互访；Week 2 若改 schema，常需 **重建 + 清卷**（见下文 Important Notes）。

## Pipeline Architecture

```
arXiv Search Query → Rate Limited API Calls → PDF Downloads → Docling Parsing → Database Storage
        ↓                    ↓                    ↓              ↓               ↓
   Date Filtering    →  Retry Logic       →   Caching      → Structure    →  Upsert Logic
   Category Filter   →  Error Handling    →   Validation   → Extraction   →  Transactions
   Result Limiting   →  3s Rate Limit     →   Size Checks  → Metadata     →  Relationships
```

> **中文 · 上图怎么读：** 从左到右是 **数据流动方向**；第二行是各阶段的 **工程手段**（过滤、重试、校验、事务等）。

## Performance Characteristics

**Week 2 System Capabilities:**
- **arXiv API**: ~20 papers/minute (respecting 3-second rate limits)
- **PDF Processing**: 2-5 seconds per paper (depends on PDF complexity)
- **Database Storage**: ~100 papers/second (batch operations)
- **Error Handling**: Graceful continuation despite individual failures
- **Success Rates**: 95%+ for paper fetching, 80-90% for PDF parsing

> **中文 · 性能预期：** 拉取受 **官方限流** 约束；解析耗时与 **页数、图表** 相关；单篇失败不应拖垮整批；**解析成功率 80–90%** 在学术论文场景很常见。

## Target Audience

This material is designed for:
- **Data Engineers** learning research data pipeline construction
- **Students** interested in academic research automation
- **Developers** building content aggregation systems
- **Researchers** wanting to automate literature discovery
- **Anyone** building production data ingestion pipelines

> **中文 · 适合人群：** 想搭 **学术文献自动化** 流水线的数据工程/开发/研究者；不要求事先精通 Airflow，但需能跟 Docker + Python 异步。

## Time Commitment

- **Fresh container build**: 10-15 minutes (required for Week 2 dependencies)
- **Notebook completion**: 45-60 minutes
- **Pipeline testing**: 30-45 minutes
- **Total**: 1.5-2 hours

> **中文 · 时间：** 首次 **build** 可能较久；arXiv 与 PDF 测试受 **网络** 影响；预留 **1.5–2 小时** 较稳妥。

## 📖 Additional Resources

**Week 2 Blog Post:** [Building Robust Data Pipelines for Academic Research](https://jamwithai.substack.com/p/building-data-pipelines-academic-research)
- Deep dive into arXiv API best practices
- PDF processing strategies for scientific documents
- Error handling patterns for production systems
- Database design for research metadata

> **中文 · 延伸阅读：** 博客补充 **API 礼仪**、**PDF 策略**、**错误处理模式** 与 **元数据建模**，建议 notebook 跑通后再读。

## Important Notes

### Fresh Container Build Required
Week 2 requires rebuilding containers with new dependencies:

```bash
# Shutdown and rebuild (REQUIRED for Week 2)
docker compose down
docker compose up --build

# This ensures:
# - New Python dependencies (docling, arxiv client)
# - Updated Airflow DAGs
# - Fresh service configurations
```

> **中文 · 何时重建：** 从 Week 1 切到 Week 2、或依赖/DAG 有更新时，应用 **`docker compose up --build`**（必要时加 **`-d`** 后台运行）；若 **数据库 schema 冲突**，见下一小节「清卷」。

### PDF Processing Expectations
- Not all PDFs parse successfully (expected behavior)
- Docling works best with standard academic paper formats
- System handles failures gracefully and continues processing
- Success rates of 80-90% are normal for academic PDFs

> **中文 · PDF 预期：** 解析失败 **不算你配置错了**；关注系统是否 **记录错误并继续**。

### Schema / 数据库从零开始（与 notebook 一致）

若你第一次跑 Week 2，或遇到 **列缺失 / schema 不一致**，可用「清卷 + 重建」（会 **删除容器卷内数据**）：

```bash
docker compose down -v
docker compose up --build -d
```

> **中文：** 与 `week2_arxiv_integration.ipynb` 中 **IMPORTANT: Week 2 Database Schema Update** 小节说明一致；**仅当** 你不介意清空本地实验数据时使用。

## Support Resources

If you encounter issues:
1. Ensure fresh containers are built (`docker compose up --build`)
2. Check the troubleshooting sections in the notebook
3. Review service health checks and logs
4. Verify all Week 1 infrastructure is working
5. Ask in Jam With AI substack chat channel

> **中文 · 排错顺序：** 先 **compose 是否 build 成功** → notebook 健康检查 → **`docker compose logs <服务名>`** → 对照 Week 1 是否仍正常 → 社区提问。

## Next Steps

After completing Week 2, you will be ready to:
- Understand production data pipeline architecture
- Handle real-world API integration challenges
- Implement robust error handling and monitoring
- Proceed to Week 3: OpenSearch Integration and Full-Text Search
- Build confidence in handling complex data processing workflows

> **中文 · 下一周：** Week 3 将把论文与块 **写入 OpenSearch** 并做 **BM25 等全文检索**，本周入库的数据会成为检索底座。

## Success Criteria

✅ **Week 2 Complete When:**
- arXiv API client fetches papers with proper rate limiting
- PDF download and caching works reliably
- Docling parser extracts structured content from scientific papers
- Database stores complete paper metadata with relationships
- Complete pipeline processes papers end-to-end with error handling
- Airflow DAGs are configured and ready for automation
- All components demonstrate production-grade error handling and monitoring

> **中文 · 完成标准：** arXiv 能稳定拉取；PDF 能下载到缓存；Docling 在 **部分** PDF 上成功即可；数据库 **upsert + 读回** 正常；流水线小批量 **端到端** 可跑通；Airflow 中能看到相关 DAG（即使个别环境有导入告警，也应理解原因）。
