FROM python:3.12-slim

WORKDIR /workspace

# Install uv from official image (faster and more reliable than curl install)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml ./
COPY README.md ./
COPY src/ ./src/
COPY tests/ ./tests/
COPY tools/ ./tools/
COPY webhook_server.py ./

# Install Python dependencies with uv
ARG INSTALL_TEST_DEPS=false
RUN if [ "$INSTALL_TEST_DEPS" = "true" ]; then \
        uv pip install --system -e ".[dev]" pytest-xdist; \
    else \
        uv pip install --system -e .; \
    fi

# Default command
CMD ["python", "-c", "import asmf; print('ASMF framework loaded successfully')"]
