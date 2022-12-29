# Trassir RTSP proxy
## Basic usage

```
docker build -t trssr_rtsp_proxy github.com/Silencer2K/trssr_rtsp_proxy
docker run \
    -p 8554:8554 \
    -e API_HOST=https://<trassir_host>:8080 \
    -e RTSP_HOST=rtsp://<trassir_host>:555 \
    -e LOGIN=<login> \
    -e PASSWORD=<password> \
    -e PATHS=*
    trssr_rtsp_proxy
```
