FROM python:3.9
RUN pip install pytest
WORKDIR /app
# RUN mkdir -p /opt
COPY run.sh /opt/
COPY runtests.py /opt/
COPY modes /opt/modes/
ENTRYPOINT ["/opt/run.sh"]
