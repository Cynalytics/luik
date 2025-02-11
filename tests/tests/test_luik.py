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
    assert response.text == "OK"


def test_luik_pop(api: TestClient) -> None:
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


def test_luik_boefje_input(api: TestClient) -> None:
    task_id = "99b5e767-bdd9-4805-9f66-24ebc4520919"
    response = api.get(f"/boefje/input/{task_id}")

    boefje_input = json.loads(response.content)
    assert response.is_success
    assert boefje_input["task_id"] == task_id

    with pytest.raises(Exception):
        _ = api.get("/boefje/input/non_existing_task")


def test_luik_boefje_output(api: TestClient) -> None:
    task_id = "99b5e767-bdd9-4805-9f66-24ebc4520919"
    req = LuikBoefjeOutputRequest(
        status="COMPLETED", files=[RawFile(tags=[], content="aGVsbG8gdGhlcmVkZGFzZGFz")]
    )

    response = api.post(f"/boefje/output/{task_id}", json=req.model_dump())
    assert response.status_code == 200

    with pytest.raises(Exception):
        response = api.post("/boefje/output/non_existing_task", json=req.model_dump())
