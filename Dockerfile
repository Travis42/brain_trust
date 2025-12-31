FROM python:3.14

# 1. System deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        git \
    && rm -rf /var/lib/apt/lists/*

# 2. Set working directory
WORKDIR /app

# 3. Copy & install Python deps first (keeps Docker layer cache effective)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy *everything else* from the project into the container
COPY . .

# 5. Default command (VS Code-friendly)
CMD ["bash"]
