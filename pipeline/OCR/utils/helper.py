import uuid
import os

def generate_uuid():
    return str(uuid.uuid4())

def get_extension(filename):
    return os.path.splitext(filename)[1].lower()