FROM aler9/rtsp-simple-server AS rtsp
FROM python:3.9

COPY --from=rtsp rtsp-simple-server .
COPY --from=rtsp rtsp-simple-server.yml .

COPY updater.py .
COPY requirements.txt .
COPY config.yml .

RUN pip install --no-cache-dir -r requirements.txt
RUN cat config.yml >> rtsp-simple-server.yml

EXPOSE 8554

ENV API_HOST=https://<trassir_host>:8080
ENV RTSP_HOST=rtsp://<trassir_host>:555

ENV LOGIN=<login>
ENV PASSWORD=<password>

ENV PATHS=*

ENTRYPOINT [ "./rtsp-simple-server" ]
