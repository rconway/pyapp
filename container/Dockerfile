# Use official Python base image
FROM python:3.13-slim

# Runtime defaults for safer, cleaner container execution
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
  && rm /tmp/requirements.txt

# Create a non-root runtime user with stable IDs
RUN addgroup --system --gid 10001 app \
  && adduser --system --uid 10001 --ingroup app --home /home/app app

# Copy app code
COPY --chown=app:app src /app

# Default port (override with -e PORT=...)
ENV PORT=8000

# Ensure imports resolve even when runtime cwd is not /app (e.g. Apptainer)
ENV PYTHONPATH=/app

# Expose default app port
EXPOSE 8000

# Basic liveness check without adding curl/wget dependencies
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import os,sys,urllib.request; port=os.getenv('PORT','8000'); urllib.request.urlopen(f'http://127.0.0.1:{port}/world', timeout=3)" || exit 1

# Run as non-root user
USER app

# Run with Uvicorn (exec ensures proper signal handling as PID 1)
CMD ["sh", "-c", "exec uvicorn --app-dir /app main:app --host 0.0.0.0 --port ${PORT:-8000}"]
