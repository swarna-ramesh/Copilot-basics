import pytest
from fastapi.testclient import TestClient

def test_get_activities(client: TestClient):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0

    # Check that each activity has the required fields
    for activity_name, activity_data in data.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)

def test_signup_for_activity_success(client: TestClient):
    """Test successful signup for an activity"""
    # First get activities to find one to test with
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]

    # Test signup
    email = "test@example.com"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]

    # Verify the participant was added
    response = client.get("/activities")
    activities = response.json()
    assert email in activities[activity_name]["participants"]

def test_signup_for_activity_already_signed_up(client: TestClient):
    """Test signup when student is already signed up"""
    # First get activities
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]

    # Sign up first time
    email = "duplicate@example.com"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Try to sign up again
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400

    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]

def test_signup_for_nonexistent_activity(client: TestClient):
    """Test signup for an activity that doesn't exist"""
    response = client.post("/activities/NonexistentActivity/signup?email=test@example.com")
    assert response.status_code == 404

    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]

def test_unregister_from_activity_success(client: TestClient):
    """Test successful unregister from an activity"""
    # First get activities and sign up
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]

    email = "unregister@example.com"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Now unregister
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]

    # Verify the participant was removed
    response = client.get("/activities")
    activities = response.json()
    assert email not in activities[activity_name]["participants"]

def test_unregister_from_activity_not_signed_up(client: TestClient):
    """Test unregister when student is not signed up"""
    # First get activities
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]

    email = "notsignedup@example.com"
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 400

    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"]

def test_unregister_from_nonexistent_activity(client: TestClient):
    """Test unregister from an activity that doesn't exist"""
    response = client.delete("/activities/NonexistentActivity/unregister?email=test@example.com")
    assert response.status_code == 404

    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]