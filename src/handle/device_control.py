import os
import json
import sys

import json

from pathlib import Path

from typing import *
from flask import Blueprint, request, Response, abort

parent_dir_path = str(Path(__file__).resolve().parents[2])
sys.path.append(parent_dir_path + "/src/event")
sys.path.append(parent_dir_path + "/src/event/modules")
sys.path.append(parent_dir_path + "/src/handle/modules")
sys.path.append(parent_dir_path + "/src/nats")

from preflight_check import cors_preflight_response
from control_body_generate import body_generate
from FileIO import dict2json

control_bp = Blueprint("control_bp", __name__)


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
    return cors_preflight_response()


@control_bp.route("/", methods=["GET", "POST", "OPTIONS"])
def control():
    if request.method == "OPTIONS":
        return cors_preflight_response()
    elif request.method == "POST":
        return post_control(request.data)
    elif request.method == "GET":
        return get_control()
    else:
        abort(404)
