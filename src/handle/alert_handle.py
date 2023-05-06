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

alert_handle_bp = Blueprint("alert_handle_bp", __name__)
database_url = CurrentEnv.DatabaseEndpoint

database_alert_db = {}


def alert_sync(request_data: Request):
    global database_alert_db

    webhook_data = request_data.data.decode()
    webhook_data = json.loads(webhook_data)

    alert_list_range = len(webhook_data["alerts"])

    for x in range(alert_list_range):
        timestamp = time.time() * 1000
        if webhook_data["status"] == "firing":
            database_alert_db.update(
                {
                    str(timestamp): {
                        "ERR": webhook_data["alerts"][x]["labels"]["ERR"],
                        "device_SN": webhook_data["alerts"][x]["labels"]["device_SN"],
                        "type": "error",
                    }
                }
            )
        elif webhook_data["status"] == "resolved":
            database_alert_db.update(
                {
                    str(timestamp): {
                        "ERR": webhook_data["alerts"][x]["labels"]["ERR"],
                        "device_SN": webhook_data["alerts"][x]["labels"]["device_SN"],
                        "type": "resolved",
                    }
                }
            )
        else:
            pass

    return_data = {}

    response = Response()
    response.response = json.dumps(return_data)
    response.headers.pop("Content-Type")
    response.headers.add("Content-Type", "application/json")
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


def alert_popup():
    global database_alert_db

    if len(database_alert_db) == 0:
        return_data = {}
    else:
        first_key = list(database_alert_db.keys())[0]

        return_data = database_alert_db[first_key]
        database_alert_db.pop(first_key)

    response = Response()
    response.response = json.dumps(return_data)
    response.headers.pop("Content-Type")
    response.headers.add("Content-Type", "application/json")
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


@alert_handle_bp.route("/", methods=["GET", "POST", "OPTIONS"])
def alert_webhook_recieve():
    if request.method == "OPTIONS":
        return cors_preflight_response()
    elif request.method == "POST":
        return alert_sync(request)
    elif request.method == "GET":
        return alert_popup()
    else:
        abort(404)
