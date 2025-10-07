FROM debian:bullseye-slim
RUN apt-get update && \
    apt-get install -y build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
COPY run.sh /usr/local/bin/run.sh
RUN chmod +x /usr/local/bin/run.sh
RUN useradd -m -s /bin/bash appuser
USER appuser
WORKDIR /app
ENTRYPOINT ["/usr/local/bin/run.sh"]
