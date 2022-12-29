# Trassir RTSP proxy
## Basic usage

1. Clone
   ```
   git clone git@github.com:Silencer2K/trssr_rtsp_proxy.git
   cd trssr_rtsp_proxy
   ```
2. Build
   ```
   docker build -t trssr_rtsp_proxy .
   ```
3. Run
   ```
   docker run \
     -p 8554:8554 \
     -e API_HOST=https://<trassir_host>:8080 \
     -e RTSP_HOST=rtsp://<trassir_host>:555 \
     -e LOGIN=<login> \
     -e PASSWORD=<password> \
     -e PATHS=*
     trssr_rtsp_proxy
   ```
