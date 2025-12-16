FROM python:3.12-slim

WORKDIR /workspace

# Install uv from official image (faster and more reliable than curl install)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files (including tools/ and webhook_server.py for tests)
# Updated 2025-12-15 to include new test dependencies
COPY pyproject.toml ./
COPY README.md ./
COPY src/ ./src/
COPY tests/ ./tests/
COPY tools/ ./tools/
COPY webhook_server.py ./

# Add workspace to PYTHONPATH so tests can import tools and webhook_server
ENV PYTHONPATH="/workspace:${PYTHONPATH}"

# Install Python dependencies with uv
ARG INSTALL_TEST_DEPS=false
RUN if [ "$INSTALL_TEST_DEPS" = "true" ]; then \
        uv pip install --system -e ".[dev]" pytest-xdist; \
    else \
        uv pip install --system -e .; \
    fi

# Set PYTHONPATH to make tools and webhook_server importable
ENV PYTHONPATH="/workspace:${PYTHONPATH}"

# Default command
CMD ["python", "-c", "import asmf; print('ASMF framework loaded successfully')"]
