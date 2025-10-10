FROM debian:bullseye-slim
RUN apt-get update && \
    apt-get install -y build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir /app
RUN useradd -m -s /bin/bash appuser
RUN chown -R appuser:appuser /app
COPY run.sh /usr/local/bin/run.sh
RUN chmod +x /usr/local/bin/run.sh
WORKDIR /app
USER appuser
ENTRYPOINT ["/usr/local/bin/run.sh"]