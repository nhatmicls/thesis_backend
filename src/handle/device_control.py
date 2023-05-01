import asyncio
import os
import json
import sys

import snappy
import json

from pathlib import Path

from typing import *
from flask import Blueprint, request, Response

parent_dir_path = str(Path(__file__).resolve().parents[2])
sys.path.append(parent_dir_path + "/src/event")
sys.path.append(parent_dir_path + "/src/event/modules")
sys.path.append(parent_dir_path + "/src/nats")

from control_body_generate import body_generate
from FileIO import dict2json

control_bp = Blueprint("control_bp", __name__)
event_loop = asyncio.new_event_loop()


def cors_preflight_response():
    response = Response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


def post_control(body):
    body_json = body.decode("utf8").replace("'", '"')
    data = json.loads(body_json)

    new_data = body_generate(
        target_control=data["data"]["target_control"],
        object_control=data["data"]["object_control"],
        status=data["data"]["status"],
    )

    dict2json(data=new_data, direct_path="./tmp.json")

    command_line = (
        "python ./src/nats/nats_send_event.py"
        + " -s nats://pifclub.ddns.net:4222/"
        + " -C ./creds/pc.creds"
        + " -c ./cert/thesis/client.crt"
        + " -k ./cert/thesis/client.key"
        + " -r ./cert/thesis/rootCA.crt"
        + " -t thesis.hcmut.data-download.hi"
        + " -d ./tmp.json"
    )
    os.system(command_line)

    return cors_preflight_response()


def get_control():
    return "<p>c</p>"


@control_bp.route("/", methods=["GET", "POST", "OPTIONS"])
def control():
    if request.method == "OPTIONS":
        return cors_preflight_response()
    elif request.method == "POST":
        return post_control(request.data)
