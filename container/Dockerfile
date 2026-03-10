# Use official Python base image
FROM python:3.13-slim

# Install dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
  && rm /tmp/requirements.txt

# Copy app code
COPY src /app

# Default port (override with -e PORT=...)
ENV PORT=8000

# Ensure imports resolve even when runtime cwd is not /app (e.g. Apptainer)
ENV PYTHONPATH=/app

# Expose default app port
EXPOSE 8000

# Run with Uvicorn (exec ensures proper signal handling as PID 1)
CMD ["sh", "-c", "exec uvicorn --app-dir /app main:app --host 0.0.0.0 --port ${PORT:-8000}"]
