FROM ghcr.io/sparfenyuk/mcp-proxy:latest

# Install required packages
RUN apk add gcc musl-dev linux-headers && pip install psutil && apk del gcc musl-dev linux-headers
RUN python3 -m ensurepip && pip install -U --no-cache-dir mcp[cli] requests docker

ENV PATH="/usr/local/bin:$PATH" \
    UV_PYTHON_PREFERENCE=only-system

ENTRYPOINT [ "mcp-proxy" ]
