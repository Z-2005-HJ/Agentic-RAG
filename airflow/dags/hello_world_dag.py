# Bilingual comments policy / 双语注释策略：保留英文注释与 docstring；中文为补充释义。
from datetime import datetime, timedelta

import psycopg2
import requests
from airflow import DAG
from airflow.operators.python import PythonOperator


def hello_world():
    """Simple hello world function.

    中文：最小示例任务，用于验证 Airflow 能调度 Python 可调用对象。
    """
    print("Hello from Airflow! Week 1 is working.")
    return "success"


def check_services():
    """Check if other services are accessible.

    中文：检查同网络内 API 与 PostgreSQL 是否可达（用于第 1 周联通性验证）。
    """
    try:
        # Check API health  # 检查 API 健康接口
        response = requests.get("http://rag-api:8000/api/v1/health", timeout=5)
        print(f"API Health: {response.status_code}")

        # Check database connection  # 检查数据库连接
        conn = psycopg2.connect(host="postgres", port=5432, database="rag_db", user="rag_user", password="rag_password")
        print("Database: Connected successfully")
        conn.close()

        return "Services are accessible"
    except Exception as e:
        print(f"Service check failed: {e}")
        raise


# DAG configuration  # DAG 默认参数（重试、起始日期等）
default_args = {
    "owner": "rag",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# Create the DAG  # 创建 DAG 实例（第 1 周 Hello World）
dag = DAG(
    "hello_world_week1",
    default_args=default_args,
    description="Hello World DAG for Week 1",
    schedule=None,
    catchup=False,
    tags=["week1", "testing"],
)

# Define tasks  # 定义任务（PythonOperator）
hello_task = PythonOperator(
    task_id="hello_world",
    python_callable=hello_world,
    dag=dag,
)

service_check_task = PythonOperator(
    task_id="check_services",
    python_callable=check_services,
    dag=dag,
)

# Set task dependencies  # 任务依赖：先 hello，再检查服务
hello_task >> service_check_task
