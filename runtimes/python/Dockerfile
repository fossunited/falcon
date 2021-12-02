FROM python:3.9
RUN pip install pytest
WORKDIR /app
RUN mkdir -p /opt
ADD run.sh /opt
ADD runtests.py /opt
ENTRYPOINT ["/opt/run.sh"]
