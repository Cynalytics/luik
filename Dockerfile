ARG PYTHON_VERSION=3.11
FROM python:$PYTHON_VERSION AS dev

ARG USER_UID=1000
ARG USER_GID=1000

RUN groupadd --gid "$USER_GID" nonroot
RUN adduser --disabled-password --gecos '' --uid "$USER_UID" --gid "$USER_GID" nonroot

WORKDIR /app/luik
ENV PATH=/home/nonroot/.local/bin:${PATH}

ARG ENVIRONMENT

COPY luik/requirements-dev.txt luik/requirements.txt ./

RUN --mount=type=cache,target=/root/.cache \
    pip install --upgrade pip \
    && if [ "$ENVIRONMENT" = "dev" ]; \
    then \
    grep -v git+https:// requirements-dev.txt | pip install -r /dev/stdin && \
    grep git+https:// requirements-dev.txt | pip install -r /dev/stdin ; \
    else \
    grep -v git+https:// requirements.txt | pip install -r /dev/stdin && \
    grep git+https:// requirements.txt | pip install -r /dev/stdin ; \
    fi

FROM dev

COPY octopoes/ /tmp/octopoes
RUN cd /tmp/octopoes && python setup.py bdist_wheel
RUN pip install /tmp/octopoes/dist/octopoes*.whl

COPY luik/entrypoint.sh .
COPY luik/luik ./luik


ENTRYPOINT ["python", "-m", "luik"]
