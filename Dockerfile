FROM python:3.10-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends coreutils && rm -rf /var/lib/apt/lists/*

COPY . .
RUN pip install --no-cache-dir .


ENV PYTHONUNBUFFERED=1 PYTHONPATH=/app

# stdbuf forces line-buffered stdout/stderr; helpful when piping through Claude
ENTRYPOINT ["stdbuf", "-oL", "-eL", "python", "-m", "thehive_mcp.main"]
CMD ["--transport", "stdio"]
