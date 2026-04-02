import pytest

@pytest.fixture(scope="module")
def admin_token(client):
    client.post(
        "/auth/register",
        json={"name": "Admin User", "email": "admin_test@example.com", "password": "password123", "role": "admin"}
    )
    response = client.post(
        "/auth/login",
        json={"email": "admin_test@example.com", "password": "password123"}
    )
    return response.json()["access_token"]


def test_create_record(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.post(
        "/records/",
        json={
            "amount": 100.50,
            "type": "expense",
            "category": "Food",
            "date": "2025-10-15",
            "description": "Lunch"
        },
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 100.50
    assert data["category"] == "Food"

def test_get_records(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/records/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_search_records(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/records/?q=Lunch", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["description"] == "Lunch"

def test_soft_delete_record(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # First get the record created above (we know it's at index 0 relative to search)
    records_res = client.get("/records/", headers=headers)
    record_id = records_res.json()[0]["id"]
    
    # Delete it
    del_res = client.delete(f"/records/{record_id}", headers=headers)
    assert del_res.status_code == 204
    
    # Verify it doesn't show up in listings
    check_res = client.get(f"/records/{record_id}", headers=headers)
    assert check_res.status_code == 404
