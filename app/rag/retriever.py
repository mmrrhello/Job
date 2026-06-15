"""
app/rag/retriever.py
Milvus 向量检索封装，支持 scalar filter (MilvusClient)。
"""
from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pymilvus import MilvusClient

from app.config import settings


@lru_cache(maxsize=1)
def _get_client() -> MilvusClient:
    client = MilvusClient(uri=f"http://{settings.milvus_host}:{settings.milvus_port}")
    client.load_collection(settings.milvus_collection)
    return client


OUTPUT_FIELDS = [
    "chunk_id", "job_id", "chunk_type", "text",
    "company", "industry", "job_title", "city",
    "min_salary", "max_salary", "education", "experience",
    "publish_date", "year",
]


def search_similar_jobs(
    query_vector: list[float],
    top_k: int = 5,
    city: Optional[str] = None,
    industry: Optional[str] = None,
    education: Optional[str] = None,
    chunk_type: Optional[str] = None,   # "summary" | "description" | None(全部)
) -> list[dict]:
    """
    向量相似度检索，支持城市/行业/学历过滤。
    返回 list[dict]，每个 dict 包含 chunk 字段 + score。
    """
    client = _get_client()

    # 构造 scalar filter 表达式
    filters = []
    if city:
        filters.append(f'city == "{city}"')
    if industry:
        filters.append(f'industry == "{industry}"')
    if education:
        filters.append(f'education == "{education}"')
    if chunk_type:
        filters.append(f'chunk_type == "{chunk_type}"')

    expr = " && ".join(filters) if filters else ""

    search_params = {
        "metric_type": "COSINE",
        "params": {"ef": 64},   # HNSW 检索参数
    }

    results = client.search(
        collection_name=settings.milvus_collection,
        data=[query_vector],
        anns_field="vector",
        search_params=search_params,
        limit=top_k,
        filter=expr or "",
        output_fields=OUTPUT_FIELDS,
    )

    hits = []
    for hit in results[0]:
        hits.append({
            "chunk_id":    hit.get("chunk_id", ""),
            "job_id":      hit.get("job_id", ""),
            "chunk_type":  hit.get("chunk_type", ""),
            "text":        hit.get("text", ""),
            "company":     hit.get("company", ""),
            "industry":    hit.get("industry", ""),
            "job_title":   hit.get("job_title", ""),
            "city":        hit.get("city", ""),
            "min_salary":  hit.get("min_salary", 0.0),
            "max_salary":  hit.get("max_salary", 0.0),
            "education":   hit.get("education", ""),
            "experience":  hit.get("experience", ""),
            "publish_date":hit.get("publish_date", ""),
            "year":        hit.get("year", 0),
            "score":       round(float(hit.get("distance", 0)), 4),
        })
    return hits
