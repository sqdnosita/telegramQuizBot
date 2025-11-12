FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

COPY pyproject.toml .
COPY .python-version .

RUN uv sync --frozen

COPY bot/ ./bot/
COPY main.py .
COPY seed_data.py .
COPY reset_db.py .

RUN mkdir -p /app/data /app/logs

ENV PYTHONUNBUFFERED=1
ENV DATABASE_PATH=/app/data/quiz_bot.db

RUN useradd -m -u 1000 botuser && \
    chown -R botuser:botuser /app
USER botuser

CMD ["uv", "run", "python", "main.py"]
