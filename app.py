import asyncio
import sys
from pathlib import Path

from typing import *
from flask import Flask

parent_dir_path = str(Path(__file__).resolve().parents[0])
sys.path.append(parent_dir_path + "/src/nats")
sys.path.append(parent_dir_path + "/src/handle")

from device_control import control_bp
from database_handle import database_handle_bp
from backend_test import backend_bp

app = Flask(__name__)
app.register_blueprint(control_bp, url_prefix="/control")
app.register_blueprint(database_handle_bp, url_prefix="/database")
app.register_blueprint(backend_bp, url_prefix="/")


@app.get("/test")
def test_site():
    return "<p>a</p>"


@app.get("/")
def homepage():
    return "<p>a</p>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
