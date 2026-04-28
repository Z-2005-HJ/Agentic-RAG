"""
用于混合搜索的 OpenSearch 索引配置（BM25 关键词搜索 + 向量搜索）。
该配置同时支持：
1. 关键词搜索（BM25算法）
2. 向量相似度搜索（使用 HNSW 算法进行近似最近邻查找）
"""

ARXIV_PAPERS_CHUNKS_INDEX = "arxiv-papers-chunks"

#定义数据怎么存、哪些字段能搜索，开启向量搜索、定义分词器、定义所有字段、配置向量索引
ARXIV_PAPERS_CHUNKS_MAPPING = {
    "settings": {
        "number_of_shards": 1,
        #分片数量 = 1
        "number_of_replicas": 0,
        #副本数量 = 0
        "index.knn": True,  # 开启向量搜索功能
        "index.knn.space_type": "cosinesimil",  # 使用余弦相似度计算向量距离
        "analysis": {
            "analyzer": {
                # 标准分词器（用于作者、标题等结构化字段）
                "standard_analyzer": {"type": "standard", "stopwords": "_english_"},
                # 文本分词器（用于正文内容，支持小写、去停用词、英文词干提取）
                "text_analyzer": {"type": "custom", "tokenizer": "standard", "filter": ["lowercase", "stop", "snowball"]},
            }
        },
    },
    "mappings": {
        "dynamic": "strict",  # 严格模式，禁止自动添加新字段
        "properties": {
            "chunk_id": {"type": "keyword"},  # 分块唯一ID
            "arxiv_id": {"type": "keyword"},  # 论文arXiv编号
            "paper_id": {"type": "keyword"},  # 论文内部ID
            "chunk_index": {"type": "integer"},  # 分块序号
            "chunk_text": {  # 分块文本内容
                "type": "text",
                "analyzer": "text_analyzer",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "chunk_word_count": {"type": "integer"},  # 分块单词数量
            "start_char": {"type": "integer"},  # 文本起始位置
            "end_char": {"type": "integer"},  # 文本结束位置
            "embedding": {  # 向量嵌入（核心向量字段）
                "type": "knn_vector",
                "dimension": 1024,  # Jina v3 模型向量维度
                "method": {
                    "name": "hnsw",  # 使用HNSW高效向量检索算法
                    "space_type": "cosinesimil",  # 余弦相似度
                    "engine": "nmslib",
                    "parameters": {
                        "ef_construction": 512,  # 构建索引精度（越高越准，速度越慢）
                        "m": 16,  # 每个节点连接数
                    },
                },
            },
            "title": {  # 论文标题
                "type": "text",
                "analyzer": "text_analyzer",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "authors": {  # 作者
                "type": "text",
                "analyzer": "standard_analyzer",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "abstract": {"type": "text", "analyzer": "text_analyzer"},  # 摘要
            "categories": {"type": "keyword"},  # 论文分类
            "published_date": {"type": "date"},  # 发布日期
            "section_title": {"type": "keyword"},  # 章节标题
            "embedding_model": {"type": "keyword"},  # 使用的向量模型
            "created_at": {"type": "date"},  # 创建时间
            "updated_at": {"type": "date"},  # 更新时间
        },
    },
}

#把 BM25（关键词）和 KNN（向量）的结果，用 RRF 算法智能融合
HYBRID_RRF_PIPELINE = {
    "id": "hybrid-rrf-pipeline",
    "description": "混合搜索结果后处理流水线（RRF 排序融合）",
    "phase_results_processors": [
        {
            "score-ranker-processor": {
                "combination": {
                    "technique": "rrf",  # 排序倒数融合（自动平衡关键词与向量结果）
                    "rank_constant": 60,  # RRF 公式参数：1/(k+rank)
                }
            }
        }
    ],
}