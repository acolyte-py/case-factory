import datetime

from fastapi.testclient import TestClient
from fastapi import status

from main import app


client = TestClient(app)


def test_send_message():
    newsletter_data = {
        "start_time": "2023-05-30T10:00:00",
        "message": "test-message",
        "filter_operation_code": "33",
        "filter_tag": "message",
        "end_time": "2023-05-31T12:00:00",
        "time_interval": "test-message",
    }

    response_n = client.post("/newsletters", json=newsletter_data)
    assert response_n.status_code == status.HTTP_200_OK
    n = response_n.json()

    client_data = {
        "phone_number": "+333",
        "operator_code": "000",
        "tag": "test-msg",
        "timezone": "+4"
    }

    response_c = client.post("/clients", json=client_data)
    assert response_c.status_code == status.HTTP_200_OK
    c = response_c.json()

    message_data = {
        "text_msg": "Test message",
        "send_time": datetime.datetime.now().isoformat(),
        "status": "отправлено",
        "newsletter_id": n["id"],
        "client_id": c["id"]
    }

    response = client.post("/messages", json=message_data)
    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()

    assert response_json["text_msg"] == message_data["text_msg"]
    assert response_json["send_time"] == message_data["send_time"]
    assert response_json["status"] == message_data["status"]
    assert response_json["newsletter_id"] == message_data["newsletter_id"]
    assert response_json["client_id"] == message_data["client_id"]