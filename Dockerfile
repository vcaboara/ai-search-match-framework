FROM python:3.12-slim

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY README.md ./
COPY src/ ./src/
COPY tests/ ./tests/

# Install Python dependencies
ARG INSTALL_TEST_DEPS=false
RUN pip install --no-cache-dir --upgrade pip && \
    if [ "$INSTALL_TEST_DEPS" = "true" ]; then \
        pip install --no-cache-dir -e ".[dev]" pytest-xdist; \
    else \
        pip install --no-cache-dir -e .; \
    fi

# Default command
CMD ["python", "-c", "import asmf; print('ASMF framework loaded successfully')"]
