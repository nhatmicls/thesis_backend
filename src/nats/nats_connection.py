import asyncio
import multiprocessing
from io import FileIO
import time
import random
from urllib import parse
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrNoServers, ErrTimeout
from asyncio.events import AbstractEventLoop
from asyncio.futures import Future
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import snappy  # type: ignore

import ssl
import json

import sys
from pathlib import Path
from typing import *


def verbose(
    data_from: str,
    string_send: str,
    type_verbose: str,
):
    dt_string = time.strftime("%d/%m/%Y %H:%M:%S")
    time_now = int(time.strftime("%H")) + 7

    print(
        "["
        + data_from
        + "] "
        + dt_string
        + " ["
        + type_verbose
        + "] "
        + str(string_send)
    )


class ControlNats:
    def __init__(self) -> None:
        self.nc = NATS()
        self.event_loop = asyncio.new_event_loop()

    async def init_natsio(
        self,
        server: str = None,
        time_out: int = None,
        user_credentials_path: str = None,
        cert_file_path: str = None,
        key_file_path: str = None,
        rootCA_file_path: str = None,
    ) -> NATS:
        ssl_ctx = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
        ssl_ctx.load_verify_locations(rootCA_file_path)
        ssl_ctx.load_cert_chain(
            certfile=cert_file_path,
            keyfile=key_file_path,
        )

        async def error_cb(e: Exception):
            verbose("NATS ", str(e), "ERROR")

        async def disconnect_cb():
            verbose("NATS ", "Disconnected", "INFO")

        async def closed_cb():
            verbose("NATS ", "Closed", "INFO")

        async def discovered_server_cb():
            verbose("NATS ", "Discovered", "INFO")

        async def reconnected_cb():
            verbose("NATS ", "Reconnected", "INFO")

        await self.nc.connect(
            server,
            tls=ssl_ctx,
            user_credentials=user_credentials_path,
            connect_timeout=time_out,
            reconnect_time_wait=2,
            max_reconnect_attempts=-1,
            verbose=True,
            error_cb=error_cb,
            disconnected_cb=disconnect_cb,
            closed_cb=closed_cb,
            discovered_server_cb=discovered_server_cb,
            reconnected_cb=reconnected_cb,
        )

    async def _send_data(self, topic: str, body: Dict[str, Any]):
        data = json.dumps(body)
        data = snappy.compress(data=data)
        try:
            msg = await self.nc.publish(subject=topic, payload=data)
            print(msg)
        except asyncio.TimeoutError:
            print("Timed out waiting for response")

    def send_data(self, topic: str, body: Dict[str, Any]):
        asyncio.set_event_loop(self.event_loop)
        asyncio.get_event_loop().run_until_complete(
            self._send_data(topic=topic, body=body)
        )
