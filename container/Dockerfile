# Use official Python base image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
  && rm requirements.txt

# Copy app code
COPY src .

# Default port (override with -e PORT=...)
ENV PORT=8000

# Expose default app port
EXPOSE 8000

# Run with Uvicorn
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
