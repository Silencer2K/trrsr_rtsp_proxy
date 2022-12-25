FROM aler9/rtsp-simple-server AS rtsp
FROM python:3.9

COPY --from=rtsp rtsp-simple-server .
COPY --from=rtsp rtsp-simple-server.yml .

COPY updater.py .
COPY requirements.txt .
COPY config.yml .

RUN pip install --no-cache-dir -r requirements.txt
RUN cat config.yml >> rtsp-simple-server.yml

ENTRYPOINT [ "./rtsp-simple-server" ]
