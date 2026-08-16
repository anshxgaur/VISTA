from kafka import KafkaProducer
import json
import base64
from pathlib import Path


KAFKA_SERVER = "localhost:9092"
TOPIC_NAME = "hospital-files"

IMAGE_PATH = Path(
    r"D:\PROGRAM\VISTA2\pipeline\source\tests\patient_test.png"
)


producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda value: json.dumps(value).encode("utf-8")
)


def send_image(image_path):
    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    # Read the image as binary data
    image_bytes = image_path.read_bytes()

    # Convert binary data to Base64 so it can be sent as JSON
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    message = {
        "file_name": image_path.name,
        "file_type": "image",
        "content_type": "image/png",
        "image_data": image_base64
    }

    producer.send(TOPIC_NAME, value=message)
    producer.flush()

    print("Image sent successfully to Kafka!")
    print(f"File: {image_path.name}")


if __name__ == "__main__":
    send_image(IMAGE_PATH)