FROM ghcr.io/astral-sh/uv:0.13.6-python3.14-trixie-slim

RUN apt-get update && apt-get install -y --no-install-recommends libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 fonts-dejavu-core && rm -rf /var/lib/apt/lists/*

RUN groupadd --system --gid 10001 tessio && useradd --system --uid 10001 --gid tessio --no-create-home tessio

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN uv sync --frozen --no-dev

COPY --from=plugin . /app/plugin

ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1 TESSIO_PLUGIN_DIR=/app/plugin

USER tessio
EXPOSE 8000
CMD ["uvicorn", "app.main:create_production_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
