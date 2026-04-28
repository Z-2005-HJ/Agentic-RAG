'''
API健康检查接口的数据格式标准
用来定义服务启动后，健康检查接口返回的JSON结构
'''
from typing import Dict, Optional

from pydantic import BaseModel, Field


#定义单个服务的健康状态
class ServiceStatus(BaseModel):
    status: str = Field(..., description="Service status", example="healthy")
    message: Optional[str] = Field(None, description="Status message", example="Connected successfully")

#整体健康响应
class HealthResponse(BaseModel):
    status: str = Field(..., description="Overall health status", example="ok")
    version: str = Field(..., description="Application version", example="0.1.0")
    environment: str = Field(..., description="Deployment environment", example="development")
    service_name: str = Field(..., description="Service identifier", example="rag-api")
    services: Optional[Dict[str, ServiceStatus]] = Field(None, description="Individual service statuses")

    #展示实例JSON
    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok",
                "version": "0.1.0",
                "environment": "development",
                "service_name": "rag-api",
                "services": {
                    "database": {"status": "healthy", "message": "Connected successfully"},
                    "pdf_parser": {"status": "healthy", "message": "Docling parser ready"},
                },
            }
        }
