FROM python:3.10

WORKDIR /app/luik


COPY luik/requirements-dev.txt ./

RUN --mount=type=cache,target=/root/.cache \
    pip install --upgrade pip \
    && pip install fastapi structlog uvicorn httpx sqlalchemy pydantic pydantic-settings psycopg2


COPY ./luik ./luik


ENTRYPOINT ["python", "-m", "luik"]
