FROM python:3.12-slim

WORKDIR /app

# Install Python dependencies
COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./luik ./luik

CMD ["python", "-m", "luik"]
