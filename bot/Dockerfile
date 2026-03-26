# Bot Dockerfile - uses uv and pyproject.toml exclusively
FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy bot project files
COPY pyproject.toml ./
COPY bot.py ./
COPY config.py ./
COPY README.md ./

# Copy handlers and services directories
COPY handlers/ ./handlers/
COPY services/ ./services/

# Install dependencies using uv
RUN uv sync

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["uv", "run", "bot.py"]
