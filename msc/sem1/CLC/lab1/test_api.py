import random

import requests

from publisher import TOPICS

BASE_URL = "http://127.0.0.1:8000"


def test_create_item():
    topic = random.choice(TOPICS)
    response = requests.post(f"{BASE_URL}/items", json={"topic": topic, "value": 42.0})
    assert response.status_code == 200
    data = response.json()
    print("Create Item:", data)
    return data["id"]


def test_get_items():
    response = requests.get(f"{BASE_URL}/items")
    assert response.status_code == 200
    data = response.json()
    print("Get Items:", data)


def test_get_item_by_id(item_id):
    response = requests.get(f"{BASE_URL}/items/{item_id}")
    assert response.status_code == 200
    data = response.json()
    print("Get Item by ID:", data)


def test_update_item(item_id):
    topic = random.choice(TOPICS)
    response = requests.put(
        f"{BASE_URL}/items/{item_id}", json={"topic": topic, "value": 84.0}
    )
    assert response.status_code == 200
    data = response.json()
    print("Update Item:", data)


def test_delete_item(item_id):
    response = requests.delete(f"{BASE_URL}/items/{item_id}")
    assert response.status_code == 200
    data = response.json()
    print("Delete Item:", data)


if __name__ == "__main__":
    item_id = test_create_item()
    test_get_items()
    test_get_item_by_id(item_id)
    test_update_item(item_id)
    test_delete_item(item_id)
    test_get_items()
