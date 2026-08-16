from utils.helper import generate_uuid

def create_filename(filename):

    uid = generate_uuid()

    extension = filename.split(".")[-1]

    return f"{uid}.{extension}"