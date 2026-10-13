FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Required by repository analysis:
# - git: clone repositories
# - ca-certificates: HTTPS GitHub access
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY ai/requirements.txt /app/ai/requirements.txt

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/ai/requirements.txt

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "ai.api.main:app", "--host", "0.0.0.0", "--port", "8000"]