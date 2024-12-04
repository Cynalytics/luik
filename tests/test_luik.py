from fastapi.testclient import TestClient

from luik.models.api_models import LuikPopRequest


def test_luik_health(api: TestClient):
    response = api.get("/health")
    assert response.status_code == 200
    assert response.text == "OK"


def test_luik_pop(api: TestClient):
    request_body = LuikPopRequest(
        reachable_networks=["a"], task_capabilities=["b"]
    ).model_dump()

    print(request_body)

    response = api.post(
        "/pop/full_queue",
        json=request_body,
    )
    assert response.status_code == 200

    response = api.post(
        "/pop/full_queue",
        json=request_body,
    )
    assert response.status_code == 200

    response = api.post(
        "/pop/full_queue",
        json=request_body,
    )
    assert response.status_code == 204

    response = api.post(
        "/pop/empty_queue",
        json=request_body,
    )
    assert response.status_code == 204

    response = api.post(
        "/pop/non_existing_queue",
        json=request_body,
    )
    assert response.status_code == 204
