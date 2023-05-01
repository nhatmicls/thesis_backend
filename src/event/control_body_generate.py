import sys
from pathlib import Path

from typing import *

parent_dir_path = str(Path(__file__).resolve().parents[2])
sys.path.append(parent_dir_path + "/src/event/modules")

from FileIO import dict2json, json2dict

FORM_DATA = {
    "data": {
        "SN": "1",
        "type_register": "2",
        "register": "3",
        "new_data": "4",
    }
}


def device_nats_body_generate(
    SN: str, type_register: int, register: str, data: str
) -> Dict[str, Any]:
    body = FORM_DATA.copy()

    body["data"].update({"SN": SN})
    body["data"].update({"type_register": type_register})
    body["data"].update({"register": register})
    body["data"].update({"data": data})

    return body


def body_generate(target_control, object_control, status):
    return device_nats_body_generate(
        SN=target_control, type_register=4, register=object_control, data=status
    )
