FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS base

WORKDIR /app

# 复制依赖声明文件
COPY pyproject.toml uv.lock ./

# UV_COMPILE_BYTECODE：生成 .pyc，加快应用启动。
# UV_LINK_MODE=copy：缓存与安装目录不在同一文件系统时避免硬链接相关告警。
# 提高 HTTP 超时与重试次数，便于在不稳定网络下拉取较大依赖。
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_HTTP_TIMEOUT=300 UV_HTTP_RETRIES=5

# 默认 PyPI 源；内网或受限环境可覆盖，例如：
# docker compose build --build-arg UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple api
ARG UV_INDEX_URL=https://pypi.org/simple
ENV UV_INDEX_URL=${UV_INDEX_URL}

# uv.lock 中的包指向 files.pythonhosted.org；部分校园网对该域名 TLS 不稳定。
# 若使用国内镜像构建，可设 UV_REWRITE_HOSTED_PACKAGES=true（与上方 UV_INDEX_URL 配合）。
ARG UV_REWRITE_HOSTED_PACKAGES=false
RUN if [ "$UV_REWRITE_HOSTED_PACKAGES" = "true" ]; then \
      sed -i 's|https://files.pythonhosted.org/packages|https://pypi.tuna.tsinghua.edu.cn/packages|g' uv.lock; \
    fi

# 安装依赖（不使用仅 BuildKit 支持的 mount 参数）
RUN uv sync --frozen --no-dev

# 复制业务源码
COPY src /app/src

FROM python:3.12.8-slim AS final

EXPOSE 8000

# 关闭 Python 输出缓冲，便于在容器中查看日志
ENV PYTHONUNBUFFERED=1
ARG VERSION=0.1.0
ENV APP_VERSION=$VERSION

WORKDIR /app

# 从前一阶段复制虚拟环境与项目文件
COPY --from=base /app /app

# 将虚拟环境加入 PATH
ENV PATH="/app/.venv/bin:$PATH"

# 启动 FastAPI（uvicorn）
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
