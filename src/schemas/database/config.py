'''
为PostgreSQL数据库连接，定义了一套完整、规范的配置参数。
'''

from pydantic import Field
from pydantic_settings import BaseSettings
#field作用： Pydantic/Pydantic-Settings中专门用来给配置字段做“元数据标注”的工具
# 1.给字段设置默认值，要是database_url没有配置环境变量，就用这个默认值
# 2.给字段加描述description：给读代码的人看，同时配合自动文档生成工具，在文档里展示配置说明
#3.做额外的校验/约束
class PostgreSQLSettings(BaseSettings):
    database_url: str = Field(
        default="postgresql://rag_user:rag_password@localhost:5432/rag_db", description="PostgreSQL database URL"
    )
    echo_sql: bool = Field(default=False, description="Enable SQL query logging")
    #默认不打印SQL日志
    pool_size: int = Field(default=20, description="Database connection pool size")
    #默认连接池大小为20
    max_overflow: int = Field(default=0, description="Maximum pool overflow")
    #默认连接池溢出数为0
    class Config:
        env_prefix = "POSTGRES_"
    #这个类告诉程序去环境变量找"POSTGRES_"开头的，来覆盖这里的变量
