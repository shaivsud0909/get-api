import pytest


def _payload(**overrides):
    return {
        "full_name": "Jane Doe",
        "phone": "9876543210",
        "line1": "221B Baker Street",
        "city": "London",
        "state": "London",
        "postal_code": "NW16XE",
        "country": "UK",
        **overrides,
    }


async def add_address(user_client, **overrides):
    return await user_client.post("/addresses", json=_payload(**overrides))


# ── Auth guard ────────────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "method, url, kwargs",
    [
        ("post", "/addresses", {"json": _payload()}),
        ("get", "/addresses", {}),
        ("put", "/addresses/1", {"json": {"city": "X"}}),
        ("patch", "/addresses/1/select", {}),
        ("delete", "/addresses/1", {}),
    ],
)
async def test_address_routes_require_token(client, method, url, kwargs):
    response = await client.request(method.upper(), url, **kwargs)
    assert response.status_code == 401


@pytest.mark.parametrize(
    "method, url, kwargs",
    [
        ("post", "/addresses", {"json": _payload()}),
        ("get", "/addresses", {}),
        ("put", "/addresses/1", {"json": {"city": "X"}}),
        ("patch", "/addresses/1/select", {}),
        ("delete", "/addresses/1", {}),
    ],
)
async def test_address_routes_reject_admin(admin_client, method, url, kwargs):
    response = await admin_client.request(method.upper(), url, **kwargs)
    assert response.status_code == 403


# ── POST /addresses ──────────────────────────────────────────────────────────

async def test_add_address_success(user_client):
    response = await add_address(user_client)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["full_name"] == "Jane Doe"
    assert data["is_default"] is True


async def test_add_second_address_is_not_default(user_client):
    await add_address(user_client)
    response = await add_address(user_client, full_name="Second Address")
    assert response.status_code == 200
    assert response.json()["data"]["is_default"] is False


@pytest.mark.parametrize(
    "overrides",
    [
        {"full_name": ""},
        {"phone": "123"},
        {"line1": ""},
        {"city": ""},
        {"state": ""},
        {"postal_code": ""},
        {"country": ""},
    ],
    ids=["empty_name", "short_phone", "empty_line1", "empty_city", "empty_state", "empty_postal", "empty_country"],
)
async def test_add_address_invalid(user_client, overrides):
    response = await add_address(user_client, **overrides)
    assert response.status_code == 422


async def test_add_address_missing_fields(user_client):
    response = await user_client.post("/addresses", json={"full_name": "Jane"})
    assert response.status_code == 422


# ── GET /addresses ───────────────────────────────────────────────────────────

async def test_fetch_addresses_empty(user_client):
    response = await user_client.get("/addresses")
    assert response.status_code == 200
    assert response.json()["data"] == []


async def test_fetch_addresses_default_first(user_client):
    first = (await add_address(user_client, full_name="First")).json()["data"]
    second = (await add_address(user_client, full_name="Second")).json()["data"]

    response = await user_client.get("/addresses")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 2
    assert data[0]["id"] == first["id"]
    assert data[0]["is_default"] is True
    assert data[1]["id"] == second["id"]


# ── PUT /addresses/{address_id} ──────────────────────────────────────────────

async def test_edit_address_success(user_client):
    address = (await add_address(user_client)).json()["data"]
    response = await user_client.put(f"/addresses/{address['id']}", json={"city": "Manchester"})
    assert response.status_code == 200
    assert response.json()["data"]["city"] == "Manchester"


async def test_edit_address_not_found(user_client):
    response = await user_client.put("/addresses/999999", json={"city": "Manchester"})
    assert response.status_code == 404


async def test_edit_address_belongs_to_another_user(user_client, client):
    import uuid

    address = (await add_address(user_client)).json()["data"]

    other = {"email": f"other-{uuid.uuid4().hex[:10]}@example.com", "password": "OtherPass123!"}
    await client.post("/signup", json=other)
    other_token = (await client.post("/login", json=other)).json()["access_token"]

    response = await client.put(
        f"/addresses/{address['id']}",
        json={"city": "Nowhere"},
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert response.status_code == 404


async def test_edit_address_invalid_phone(user_client):
    address = (await add_address(user_client)).json()["data"]
    response = await user_client.put(f"/addresses/{address['id']}", json={"phone": "12"})
    assert response.status_code == 422


# ── PATCH /addresses/{address_id}/select ─────────────────────────────────────

async def test_select_address_success(user_client):
    first = (await add_address(user_client, full_name="First")).json()["data"]
    second = (await add_address(user_client, full_name="Second")).json()["data"]

    response = await user_client.patch(f"/addresses/{second['id']}/select")
    assert response.status_code == 200
    assert response.json()["data"]["is_default"] is True

    addresses = (await user_client.get("/addresses")).json()["data"]
    defaults = [a for a in addresses if a["is_default"]]
    assert len(defaults) == 1
    assert defaults[0]["id"] == second["id"]

    first_now = next(a for a in addresses if a["id"] == first["id"])
    assert first_now["is_default"] is False


async def test_select_address_not_found(user_client):
    response = await user_client.patch("/addresses/999999/select")
    assert response.status_code == 404


# ── DELETE /addresses/{address_id} ───────────────────────────────────────────

async def test_delete_non_default_address_keeps_default(user_client):
    first = (await add_address(user_client, full_name="First")).json()["data"]
    second = (await add_address(user_client, full_name="Second")).json()["data"]

    response = await user_client.delete(f"/addresses/{second['id']}")
    assert response.status_code == 200

    addresses = (await user_client.get("/addresses")).json()["data"]
    assert len(addresses) == 1
    assert addresses[0]["id"] == first["id"]
    assert addresses[0]["is_default"] is True


async def test_delete_default_address_promotes_another(user_client):
    first = (await add_address(user_client, full_name="First")).json()["data"]
    second = (await add_address(user_client, full_name="Second")).json()["data"]

    response = await user_client.delete(f"/addresses/{first['id']}")
    assert response.status_code == 200

    addresses = (await user_client.get("/addresses")).json()["data"]
    assert len(addresses) == 1
    assert addresses[0]["id"] == second["id"]
    assert addresses[0]["is_default"] is True


async def test_delete_last_address(user_client):
    address = (await add_address(user_client)).json()["data"]
    response = await user_client.delete(f"/addresses/{address['id']}")
    assert response.status_code == 200
    assert (await user_client.get("/addresses")).json()["data"] == []


async def test_delete_address_not_found(user_client):
    response = await user_client.delete("/addresses/999999")
    assert response.status_code == 404


async def test_delete_address_twice(user_client):
    address = (await add_address(user_client)).json()["data"]
    await user_client.delete(f"/addresses/{address['id']}")
    response = await user_client.delete(f"/addresses/{address['id']}")
    assert response.status_code == 404
