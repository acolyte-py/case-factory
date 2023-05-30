from fastapi import status
from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_post_create_newsletter():
    newsletter_data = {
        "start_time": "2023-05-30T10:00:00",
        "message": "Test newsletter message",
        "filter_operation_code": "123",
        "filter_tag": "отправлено",
        "end_time": "2023-05-31T12:00:00",
        "time_interval": "dsa",
    }

    response = client.post("/newsletters", json=newsletter_data)
    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()

    assert response_json["start_time"] == newsletter_data["start_time"]
    assert response_json["message"] == newsletter_data["message"]
    assert response_json["filter_operation_code"] == newsletter_data["filter_operation_code"]
    assert response_json["filter_tag"] == newsletter_data["filter_tag"]
    assert response_json["end_time"] == newsletter_data["end_time"]
    assert response_json["time_interval"] == newsletter_data["time_interval"]

    return response_json["id"]


def test_get_newsletters_stats():
    response = client.get("/newsletters/stats")
    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()
    assert isinstance(response_json, dict)


def test_get_id_newsletter_stats():
    newsletter_id = test_post_create_newsletter()
    response = client.get(f"/newsletters/stats/{newsletter_id}")
    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()
    assert isinstance(response_json, dict)
    assert response_json["id"] == newsletter_id
    assert "messages" in response_json


def test_update_newsletter():
    newsletter_id = test_post_create_newsletter()
    newsletter_data = {
        "start_time": "2023-05-30T10:00:00",
        "message": "Test newsletter message updated",
        "filter_operation_code": "321",
        "filter_tag": "не отправлено",
        "end_time": "2023-06-01T12:00:00",
        "time_interval": "asd",
    }

    response = client.put(f"/newsletters/{newsletter_id}", json=newsletter_data)
    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()
    assert response_json["id"] == newsletter_id
    assert response_json["message"] == newsletter_data["message"]
    assert response_json["filter_operation_code"] == newsletter_data["filter_operation_code"]
    assert response_json["filter_tag"] == newsletter_data["filter_tag"]
    assert response_json["end_time"] == newsletter_data["end_time"]
    assert response_json["time_interval"] == newsletter_data["time_interval"]


def test_delete_newsletter():
    newsletter_id = test_post_create_newsletter()
    response = client.delete(f"/newsletters/{newsletter_id}")
    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()
    assert response_json["message"] == "Newsletter deleted successfully"

