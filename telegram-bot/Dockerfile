FROM python:3.11-slim

WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN pip install --no-cache-dir \
    aiogram \
    httpx \
    pydantic \
    pydantic-settings \
    python-dotenv

# Copy application code
COPY . .

# Run the bot
CMD ["python", "-m", "app.main"]
