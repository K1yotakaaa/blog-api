FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Install Python dependencies first (layer-cache friendly)
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/base.txt

# Copy the project source code
COPY . .

# Create necessary directories (including logs)
RUN mkdir -p /app/staticfiles /app/media /app/data /app/logs && chown -R appuser:appuser /app

# Make entrypoint executable
RUN chmod +x scripts/entrypoint.sh

# Switch to non-root user
USER appuser

ENTRYPOINT ["scripts/entrypoint.sh"]

# Default command
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "settings.asgi:application"]