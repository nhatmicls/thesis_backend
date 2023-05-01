import sys
from pathlib import Path

from typing import *
from flask import Blueprint, request

backend_bp = Blueprint("backend_bp", __name__)


@backend_bp.post("/")
def post_test():
    body = request.data
    print(body)
    return "<p>b</p>"


@backend_bp.get("/")
def get_test():
    return "<p>c</p>"
