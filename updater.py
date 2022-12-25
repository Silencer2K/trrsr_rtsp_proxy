import os
import re
import time

import requests
from transliterate import translit
from urllib3.exceptions import InsecureRequestWarning

TRASSIR_API_HOST = os.environ["API_HOST"]
TRASSIR_RTSP_HOST = os.environ["RTSP_HOST"]

TRASSIR_LOGIN = os.environ["LOGIN"]
TRASSIR_PASSWORD = os.environ["PASSWORD"]

TRASSIR_STREAMS = os.environ.get("STREAMS", "")

API_HOST = "http://localhost:9997"
UPDATE_INTERVAL = 10

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


class TrassirAPI:
    def __init__(self):
        self.sid = None

    def auth(self):
        params = {"username": TRASSIR_LOGIN, "password": TRASSIR_PASSWORD}

        resp = requests.get(f"{TRASSIR_API_HOST}/login", params, verify=False)
        resp_json = resp.json()

        if resp_json.get("success", 1) == 0:
            return None

        self.sid = resp_json.get("sid", None)
        return resp_json

    def request(self, method, reauth=False, **kwargs):
        if reauth or self.sid is None:
            self.auth()
            reauth = True

        params = kwargs
        params.update({"sid": self.sid})

        resp = requests.get(f"{TRASSIR_API_HOST}/{method}", params, verify=False)
        resp_json = resp.json()

        if resp_json.get("success", 1) == 0:
            if not reauth and resp_json.get("error_code", "") == "no session":
                return self.request(method, reauth=True, **kwargs)

            return None

        return resp_json


class API:
    def get(self, method):
        resp = requests.get(f"{API_HOST}/v1/{method}")
        return resp.json()

    def post(self, method, payload=None):
        resp = requests.post(f"{API_HOST}/v1/{method}", json=payload)
        return resp.json() if len(resp.content) > 0 else None


class Updater:
    trassir_api = TrassirAPI()
    api = API()

    def get_id(self, name):
        return re.sub(r"[^0-9a-z]+", "_", translit(name, "ru", reversed=True).lower())

    def get_channels(self):
        resp = self.trassir_api.request("channels")
        return {self.get_id(e["name"]): e for e in resp["channels"]}

    def get_video(self, channel, stream):
        resp = self.trassir_api.request(
            "get_video",
            channel=channel["guid"],
            stream=stream,
            container="rtsp",
            audio="pcmu",
        )
        return f"{TRASSIR_RTSP_HOST}/{resp['token']}"

    def check(self):
        channels = self.get_channels()
        paths = self.api.get("paths/list")["items"]

        if len(TRASSIR_STREAMS) > 0:
            streams = TRASSIR_STREAMS.split(",")
        else:
            streams = []
            for channel in channels:
                if channels[channel]["have_mainstream"] == "1":
                    streams += [channel]
                if channels[channel]["have_substream"] == "1":
                    streams += [channel + "_sub"]

        for path in streams:
            channel, stream = path, "main"

            if path.endswith("_sub"):
                channel, stream = path[:-4], "sub"

            if not (
                channel in channels
                and channels[channel].get(f"have_{stream}stream", "") == "1"
            ):
                print(f"[updater] stream '{path}' is not available")
                continue

            if path in paths:
                if paths[path].get("source", None) is not None:
                    continue

                print(f"[updater] remove /{path}")
                self.api.post(f"config/paths/remove/{path}")

            source = self.get_video(channels[channel], stream)

            print(f"[updater] add /{path}: source={source}")
            self.api.post(f"config/paths/add/{path}", {"source": source})


if __name__ == "__main__":
    updater = Updater()
    while True:
        updater.check()
        time.sleep(UPDATE_INTERVAL)
