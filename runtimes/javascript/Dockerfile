FROM node:18
WORKDIR /app
RUN mkdir -p /opt/modes
COPY run.sh /opt/
COPY modes/exec.sh /opt/modes/
RUN chmod +x /opt/run.sh /opt/modes/exec.sh
ENTRYPOINT ["/opt/run.sh"]
