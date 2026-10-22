# ==============================================================================
# LendFlow FinOps Platform — Backend Dockerfile
# Python 3.11+ slim base
# ==============================================================================

FROM python:3.11-slim

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY app/backend/requirements.txt requirements.txt

# Install python packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code, datasets, and analysis modules
COPY app/ /workspace/app/
COPY data/ /workspace/data/
COPY analysis/ /workspace/analysis/
COPY presentation/ /workspace/presentation/
COPY docs/ /workspace/docs/
COPY policies/ /workspace/policies/
COPY infrastructure/ /workspace/infrastructure/

EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/workspace

CMD ["uvicorn", "app.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
