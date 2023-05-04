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
sys.path.append(parent_dir_path + "/src/env")

from preflight_check import cors_preflight_response
from control_body_generate import body_generate
from backend_env import CurrentEnv
from nats_control_event import control_signal

control_bp = Blueprint("control_bp", __name__)


def post_control(body):
    body_json = body.decode("utf8").replace("'", '"')
    data = json.loads(body_json)

    new_data = body_generate(
        target_control=data["data"]["target_control"],
        object_control=data["data"]["object_control"],
        status=data["data"]["status"],
    )

    nats_respond = control_signal(
        server=CurrentEnv.NatsioEndpoints,
        user_credentials_path=CurrentEnv.UserCredsPath,
        cert_file_path=CurrentEnv.CertTLSPath,
        key_file_path=CurrentEnv.KeyTLSPath,
        rootCA_file_path=CurrentEnv.RootCATLSPath,
        topic=CurrentEnv.NatsioTopics,
        data=new_data,
    )

    if nats_respond == 1:
        return_data = {"status": 200, "statusText": "OK"}
    else:
        return_data = {"status": 408, "statusText": "RequestTimeOut"}

    response = Response()
    response.response = json.dumps(return_data)
    response.headers.pop("Content-Type")
    response.headers.add("Content-Type", "application/json")
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


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
