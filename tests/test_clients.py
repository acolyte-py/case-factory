from fastapi.testclient import TestClient
from fastapi import status

from main import app


client = TestClient(app)


def test_post_create_client():
    client_data = {
        "phone_number": "+1234590",
        "operator_code": "000",
        "tag": "test",
        "timezone": "+4"
    }

    response = client.post("/clients", json=client_data)
    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()

    assert "id" in response_json
    assert response_json["phone_number"] == client_data["phone_number"]
    assert response_json["operator_code"] == client_data["operator_code"]
    assert response_json["tag"] == client_data["tag"]
    assert response_json["timezone"] == client_data["timezone"]

    return response_json["id"]


def test_put_update_client():
    client_data = {
        "phone_number": "+232323",
        "operator_code": "111",
        "tag": "test-adm",
        "timezone": "+4"
    }

    response = client.post("/clients", json=client_data)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    updated_data = {
        "phone_number": "+454545",
        "operator_code": "222",
        "tag": "updated",
        "timezone": "+5"
    }

    response = client.put(f"/clients/{data['id']}", json=updated_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["phone_number"] == updated_data["phone_number"]
    assert response.json()["operator_code"] == updated_data["operator_code"]
    assert response.json()["tag"] == updated_data["tag"]
    assert response.json()["timezone"] == updated_data["timezone"]
    assert response.json()["id"] == data["id"]


def test_delete_client():
    client_id = test_post_create_client()
    response_d_true = client.delete(f'/clients/{client_id}')

    assert response_d_true.status_code == status.HTTP_200_OK
    assert response_d_true.json() == {"message": "Client deleted successfully"}


def test_delete_nonexistent_client():
    response_d_false = client.delete('/clients/1000')
    assert response_d_false.status_code == status.HTTP_404_NOT_FOUND
    assert response_d_false.json()['detail'] == '[E] Client not found!'
