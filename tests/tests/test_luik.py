import json
import pytest
from fastapi.testclient import TestClient

from luik.models.api_models import (
    File as RawFile,
    LuikBoefjeOutputRequest,
    LuikPopRequest,
)


def test_luik_health(api: TestClient) -> None:
    response = api.get("/health")
    assert response.status_code == 200
    assert response.text == '"OK"'


def test_luik_pop(authenticated_api: TestClient) -> None:
    request_body = LuikPopRequest(
        reachable_networks=["a"], task_capabilities=["b"]
    ).model_dump()

    response = authenticated_api.post(
        "/pop",
        json=request_body,
    )
    assert response.status_code == 200

    response = authenticated_api.post(
        "/pop",
        json=request_body,
    )
    assert response.status_code == 200

    response = authenticated_api.post(
        "/pop",
        json=request_body,
    )
    assert response.status_code == 204

    response = authenticated_api.post(
        "/pop",
        json=request_body,
    )
    assert response.status_code == 204


def test_luik_boefje_input(authenticated_api: TestClient) -> None:
    task_id = "99b5e767-bdd9-4805-9f66-24ebc4520919"
    response = authenticated_api.get(f"/boefje/input/{task_id}")

    boefje_input = json.loads(response.content)
    assert response.is_success
    assert boefje_input["task"]["id"] == task_id

    response = authenticated_api.get(
        "/boefje/input/4b9aeb29-08a1-4a49-a0aa-84725e594d3a"
    )
    assert response.status_code == 404


def test_luik_boefje_output(authenticated_api: TestClient) -> None:
    task_id = "99b5e767-bdd9-4805-9f66-24ebc4520919"
    req = LuikBoefjeOutputRequest(
        status="COMPLETED", files=[RawFile(tags=[], content="aGVsbG8gdGhlcmVkZGFzZGFz")]
    )

    response = authenticated_api.post(
        f"/boefje/output/{task_id}", json=req.model_dump()
    )
    assert response.status_code == 200

    with pytest.raises(Exception):
        response = authenticated_api.post(
            "/boefje/output/non_existing_task", json=req.model_dump()
        )
