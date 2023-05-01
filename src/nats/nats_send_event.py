import asyncio
from urllib import parse
from nats.aio.client import Client as NATS
import json
import ssl
import argparse

import sys
from pathlib import Path

from typing import *

import snappy  # type: ignore

parent_dir_path = str(Path(__file__).resolve().parents[2])
sys.path.append(parent_dir_path + "/src/event/modules")

from FileIO import json2dict


async def init_natsio(
    server: str = None,
    user_credentials_path: str = None,
    cert_file_path: str = None,
    key_file_path: str = None,
    rootCA_file_path: str = None,
) -> NATS:
    nc = NATS()

    ssl_ctx = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
    ssl_ctx.load_verify_locations(rootCA_file_path)
    ssl_ctx.load_cert_chain(
        certfile=cert_file_path,
        keyfile=key_file_path,
    )

    async def error_cb(e):
        print("Error:", e)

    await nc.connect(
        server,
        tls=ssl_ctx,
        user_credentials=user_credentials_path,
        connect_timeout=10,
        reconnect_time_wait=2,
        max_reconnect_attempts=-1,
        error_cb=error_cb,
    )
    return nc


async def init(
    server: str,
    user_credentials_path: str,
    cert_file_path: str,
    key_file_path: str,
    rootCA_file_path: str,
    topic: str,
    data_path: str,
):
    async def cb(msg):
        msg_data = msg.data
        snappy_msg = snappy.decompress(msg_data)

    nc = await init_natsio(
        server=server,
        user_credentials_path=user_credentials_path,
        cert_file_path=cert_file_path,
        key_file_path=key_file_path,
        rootCA_file_path=rootCA_file_path,
    )

    json_data = json2dict(direct_path=data_path)
    data = snappy.compress(data=json.dumps(json_data))

    try:
        msg = await nc.request(subject=topic, payload=data, cb=cb, timeout=10)
        print(msg)
    except asyncio.TimeoutError:
        print("Timed out waiting for response")

    await nc.close()


def run(
    server,
    user_credentials_path,
    cert_file_path,
    key_file_path,
    rootCA_file_path,
    topic,
    data_path,
) -> None:
    asyncio.run(
        init(
            server,
            user_credentials_path,
            cert_file_path,
            key_file_path,
            rootCA_file_path,
            topic,
            data_path,
        )
    )


parser = argparse.ArgumentParser(description="Script so useful.")
parser.add_argument("-s", "--server", type=str)
parser.add_argument("-C", "--user_credentials_path", type=str)
parser.add_argument("-c", "--cert_file_path", type=str)
parser.add_argument("-k", "--key_file_path", type=str)
parser.add_argument("-r", "--rootCA_file_path", type=str)
parser.add_argument("-t", "--topic", type=str)
parser.add_argument("-d", "--data_path", type=str)

args = parser.parse_args()

run(
    server=args.server,
    user_credentials_path=args.user_credentials_path,
    cert_file_path=args.cert_file_path,
    key_file_path=args.key_file_path,
    rootCA_file_path=args.rootCA_file_path,
    topic=args.topic,
    data_path=args.data_path,
)
