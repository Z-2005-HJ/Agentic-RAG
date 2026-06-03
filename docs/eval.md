# RAG 离线评估

用固定问题集批量调用 API，导出 CSV 供人工打分，对比 **标准 RAG** 与 **Agentic RAG**。

## 前置条件

1. 服务已启动（Docker 或 `uv run uvicorn src.main:app`）
2. OpenSearch 中已有索引数据
3. Ollama 可用

## 快速运行

```bash
uv run python scripts/eval_rag.py
```

默认：

- 问题文件：`scripts/eval_questions.jsonl`
- API 地址：`http://localhost:8000`
- 对每个问题依次调用 `/api/v1/ask` 和 `/api/v1/ask-agentic`
- 结果 CSV：`scripts/eval_results/eval_YYYYMMDD_HHMMSS.csv`

## 常用参数

```bash
# 只测标准 RAG
uv run python scripts/eval_rag.py --standard-only

# 只测 Agentic
uv run python scripts/eval_rag.py --agentic-only

# 指定模型与 top_k
uv run python scripts/eval_rag.py --model deepseek-r1:7b --top-k 5

# 自定义输出路径
uv run python scripts/eval_rag.py --output my_eval.csv
```

## 问题集格式（JSONL）

每行一个 JSON 对象：

```json
{"query": "What is LoRA?", "notes": "optional label for your spreadsheet"}
```

可编辑 `scripts/eval_questions.jsonl` 或新建文件后用 `--questions` 指定。

## CSV 列说明

| 列 | 含义 |
|----|------|
| `query` | 测试问题 |
| `mode` | `standard` 或 `agentic` |
| `status_code` | HTTP 状态码 |
| `latency_ms` | 请求耗时（毫秒） |
| `answer` | 模型回答 |
| `sources` | 来源链接（`\|` 分隔） |
| `chunks_used` | 使用 chunk 数（标准 RAG） |
| `search_mode` | `bm25` / `hybrid` |
| `retrieval_attempts` | Agentic 检索轮次 |
| `reasoning_steps` | Agentic 推理步骤 |
| `manual_score_1_to_5` | **人工填写** 质量分 |
| `manual_comment` | **人工填写** 备注 |

## 建议评估流程

1. 跑脚本生成 CSV  
2. 在 Excel / WPS 中打开，对每条 `answer` 打 1～5 分  
3. 对比同一 `query` 下 `standard` vs `agentic` 的分数与 `latency_ms`  
4. 低分样本到 Langfuse 查 trace，看检索 chunk 是否相关  

## 简单指标（人工汇总）

- **平均 manual_score**（按 mode 分组）
- **P50 / P95 latency_ms**
- **sources 非空比例**
- **Agentic 平均 retrieval_attempts**

无需标注数据集即可做第一轮质量对比；有标注后可扩展为 Context Precision 等自动化指标。
