from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture()
def client():
    # cada teste usa uma cópia limpa da estrutura de activities
    # como activities é um dicionário global mutável, fazemos um backup e restauramos após o teste
    original = {k: {**v, "participants": list(v.get("participants", []))} for k, v in activities.items()}
    client = TestClient(app)
    yield client
    # restaurar estado
    activities.clear()
    activities.update(original)


def test_root_redirects_to_index(client):
    resp = client.get("/")
    # FastAPI's RedirectResponse gives a 307 by default for GET
    assert resp.status_code in (200, 307, 308)


def test_get_activities(client):
    resp = client.get("/activities")

from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def test_root_redirects_to_index():
    resp = client.get("/")
    # should redirect to the static index.html
    assert resp.status_code in (200, 307, 308)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # activities should be a dict and contain known keys
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_remove_participant():
    activity = "Chess Club"
    email = "tester@mergington.edu"

    # ensure not already signed up
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # sign up
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    # try signing up again -> should fail with 400
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 400

    # remove participant
    resp = client.delete(f"/activities/{activity}/participant", params={"email": email})
    assert resp.status_code == 200
    assert email not in activities[activity]["participants"]


def test_signup_nonexistent_activity():
    resp = client.post("/activities/NoSuchActivity/signup", params={"email": "a@b.c"})
    assert resp.status_code == 404
