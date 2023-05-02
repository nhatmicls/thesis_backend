import os
import time
import sys

import json
import requests

from pathlib import Path

from typing import *
from flask import Blueprint, request, Response, abort, Request, jsonify

parent_dir_path = str(Path(__file__).resolve().parents[2])
sys.path.append(parent_dir_path + "/src/event")
sys.path.append(parent_dir_path + "/src/env")
sys.path.append(parent_dir_path + "/src/event/modules")
sys.path.append(parent_dir_path + "/src/handle/modules")

from preflight_check import cors_preflight_response
from backend_env import CurrentEnv

database_handle_bp = Blueprint("database_handle_bp", __name__)
database_url = CurrentEnv.endpoint_database


def post_database(request_data: Request):
    url = (
        database_url
        + "?query="
        + request_data.args.get("query")
        + "&time="
        + str(int(time.time()))
    )
    return_data = requests.get(url=url)

    response = Response()
    response.response = return_data
    response.headers.pop("Content-Type")
    response.headers.add("Content-Type", "application/json")
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response
    # return jsonify(return_data.text)


def get_database(request_data: Request):
    url = (
        database_url
        + "?query="
        + request_data.args.get("query")
        + "&time="
        + str(int(time.time()))
    )
    return_data = requests.get(url=url)

    response = Response()
    response.response = return_data
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


@database_handle_bp.route("/", methods=["GET", "POST", "OPTIONS"])
def control():
    # print(post_database(request).data)
    if request.method == "OPTIONS":
        return cors_preflight_response()
    elif request.method == "POST":
        return post_database(request)
    elif request.method == "GET":
        return post_database(request)
    else:
        abort(404)
