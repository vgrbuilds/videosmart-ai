FROM python:3.12-slim

# Install system dependencies (including nodejs for yt-dlp signature deciphering)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency specifications
COPY pyproject.toml uv.lock ./

# Install python dependencies without writing bytecode cache
RUN uv sync --frozen --no-cache

# Copy application source code
COPY . .

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
