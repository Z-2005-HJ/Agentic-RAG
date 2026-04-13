# Bilingual comments policy / 双语注释策略：保留英文注释与 docstring；中文为补充释义。
import pytest


async def test_health_check(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "service_name" in data
    assert "version" in data
    assert "services" in data
