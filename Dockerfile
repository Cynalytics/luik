FROM python:3.12

WORKDIR /app

# System deps:
COPY ./requirements.txt ./requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Creating folders, and files for a project:
COPY ./luik ./luik

CMD ["python", "-m", "luik"]
