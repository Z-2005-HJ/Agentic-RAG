FROM python:3.12-slim

# Set environment variables
ENV AIRFLOW_HOME=/opt/airflow
ENV AIRFLOW_VERSION=2.10.3
ENV PYTHON_VERSION=3.12
ENV CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

# pip index (override on slow routes), e.g. --build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ARG PIP_INDEX_URL=https://pypi.org/simple
# docling/torch NVIDIA wheels: mirrors sometimes disagree with PyPI hashes; default to pypi.org for this layer.
ARG PIP_TASK_DEPS_INDEX_URL=https://pypi.org/simple
ENV PIP_DEFAULT_TIMEOUT=600

# Install system dependencies
# Use mirror + retries for unstable international network routes.
RUN if [ -f /etc/apt/sources.list ]; then \
      sed -i 's|http://deb.debian.org/debian|https://mirrors.tuna.tsinghua.edu.cn/debian|g; s|http://deb.debian.org/debian-security|https://mirrors.tuna.tsinghua.edu.cn/debian-security|g' /etc/apt/sources.list; \
    fi && \
    if [ -d /etc/apt/sources.list.d ]; then \
      find /etc/apt/sources.list.d -type f \( -name "*.list" -o -name "*.sources" \) -exec sed -i 's|http://deb.debian.org/debian|https://mirrors.tuna.tsinghua.edu.cn/debian|g; s|http://deb.debian.org/debian-security|https://mirrors.tuna.tsinghua.edu.cn/debian-security|g' {} +; \
    fi && \
    for i in 1 2 3 4 5; do \
      apt-get update -o Acquire::Retries=8 -o Acquire::http::Timeout=60 -o Acquire::https::Timeout=60 && break; \
      echo "apt-get update failed, retrying ($i/5)..." && sleep 10; \
    done && \
    for i in 1 2 3 4 5; do \
      apt-get install -y --fix-missing --no-install-recommends \
        -o Acquire::Retries=8 \
        -o Acquire::http::Timeout=60 \
        -o Acquire::https::Timeout=60 \
        build-essential \
        curl \
        git \
        libpq-dev \
        poppler-utils \
        tesseract-ocr && break; \
      echo "apt-get install failed, retrying ($i/5)..." && \
      dpkg --configure -a || true && \
      apt-get -f install -y || true && \
      sleep 10; \
    done && \
    rm -rf /var/lib/apt/lists/*

# Create airflow user with UID/GID 50000 for cross-platform compatibility
RUN groupadd -r -g 50000 airflow && useradd -r -u 50000 -g airflow -d ${AIRFLOW_HOME} -s /bin/bash airflow

# Create airflow directories with proper ownership
RUN mkdir -p ${AIRFLOW_HOME} && \
    mkdir -p ${AIRFLOW_HOME}/dags && \
    mkdir -p ${AIRFLOW_HOME}/logs && \
    mkdir -p ${AIRFLOW_HOME}/plugins && \
    chown -R 50000:50000 ${AIRFLOW_HOME} && \
    chmod -R 755 ${AIRFLOW_HOME}

# Install Airflow with PostgreSQL support
RUN pip install --no-cache-dir --retries 15 \
    -i "${PIP_INDEX_URL}" \
    "apache-airflow[postgres]==${AIRFLOW_VERSION}" \
    --constraint "${CONSTRAINT_URL}" \
    psycopg2-binary

# Copy requirements and install project dependencies
COPY requirements-airflow.txt /tmp/requirements-airflow.txt
RUN pip install --no-cache-dir --retries 15 \
    -i "${PIP_TASK_DEPS_INDEX_URL}" \
    -r /tmp/requirements-airflow.txt

# Copy and set up entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Switch to airflow user and set working directory
USER airflow
WORKDIR ${AIRFLOW_HOME}

# Expose port
EXPOSE 8080

CMD ["/entrypoint.sh"]