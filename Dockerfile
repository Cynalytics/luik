FROM python:3.12-slim

WORKDIR /app

# System deps:
COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Creating folders, and files for a project:
COPY ./luik ./luik

CMD ["python", "-m", "luik"]
