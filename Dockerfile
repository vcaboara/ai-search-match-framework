FROM python:3.12-slim

WORKDIR /workspace

# Install system dependencies and uv
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    curl \
    && curl -LsSf https://astral.sh/uv/install.sh | sh && \
    rm -rf /var/lib/apt/lists/*

# Add uv to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy project files
COPY pyproject.toml ./
COPY README.md ./
COPY src/ ./src/
COPY tests/ ./tests/

# Install Python dependencies with uv
ARG INSTALL_TEST_DEPS=false
RUN if [ "$INSTALL_TEST_DEPS" = "true" ]; then \
        uv pip install --system -e ".[dev]" pytest-xdist; \
    else \
        uv pip install --system -e .; \
    fi

# Default command
CMD ["python", "-c", "import asmf; print('ASMF framework loaded successfully')"]
