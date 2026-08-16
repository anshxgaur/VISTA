import json

def read_json(file_bytes):

    return json.loads(
        file_bytes.decode("utf-8")
    )