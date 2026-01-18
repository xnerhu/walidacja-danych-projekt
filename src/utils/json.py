import json
from typing import Optional


def json_stringify(obj, ident: Optional[int] = None):
    return json.dumps(obj, indent=ident)


def json_parse(s):
    return json.loads(s)


def try_parse_json(s):
    try:
        return json_parse(s)
    except Exception:
        return None
