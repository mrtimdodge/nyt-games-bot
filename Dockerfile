# Use a slim Python base
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    WDM_LOG_LEVEL=0 \
    CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Install system deps and chromium + chromedriver
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    wget \
    gnupg \
    unzip \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    chromium \
    chromium-driver \
  && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y fonts-noto-color-emoji --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -ms /bin/bash appuser
WORKDIR /app

# Install Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip setuptools wheel \
 && pip install -r /app/requirements.txt

# Copy app
COPY cogs /app/cogs
COPY games /app/games
COPY utils /app/utils
COPY models /app/models
COPY data /app/data
COPY bot.py /app/bot.py

RUN chown -R appuser:appuser /app

USER appuser
ENV PATH="/home/appuser/.local/bin:${PATH}"

# Run the bot (reads envs provided at runtime)
CMD ["python", "bot.py"]