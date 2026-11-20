import uuid

import pytest


async def create_product(admin_client, **overrides):
    payload = {"name": f"Feature Widget {uuid.uuid4().hex[:6]}", "price": 10.0, **overrides}
    resp = await admin_client.post("/add-products", json=payload)
    assert resp.status_code == 200, resp.text
    return resp.json()["data"]


async def add_feature(admin_client, product_id, **overrides):
    payload = {"key": "Material", "value": "Aluminium", **overrides}
    return await admin_client.post(f"/products-feature/{product_id}", json=payload)


# ── Auth guard ────────────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "method, url, kwargs",
    [
        ("post", "/products-feature/1", {"json": {"key": "k", "value": "v"}}),
        ("get", "/products-feature/1", {}),
        ("put", "/products-feature/1/1", {"json": {"key": "k", "value": "v"}}),
        ("delete", "/products-feature/1", {"params": {"feature_id": 1}}),
    ],
)
async def test_feature_routes_require_token(client, method, url, kwargs):
    response = await client.request(method.upper(), url, **kwargs)
    assert response.status_code == 401


@pytest.mark.parametrize(
    "method, url, kwargs",
    [
        ("post", "/products-feature/1", {"json": {"key": "k", "value": "v"}}),
        ("put", "/products-feature/1/1", {"json": {"key": "k", "value": "v"}}),
        ("delete", "/products-feature/1", {"params": {"feature_id": 1}}),
    ],
)
async def test_feature_routes_reject_user(user_client, method, url, kwargs):
    response = await user_client.request(method.upper(), url, **kwargs)
    assert response.status_code == 403


# ── POST /products-feature/{product_id} ──────────────────────────────────────

async def test_add_feature_success(admin_client):
    product = await create_product(admin_client)
    response = await add_feature(admin_client, product["id"], key="Material", value="Aluminium")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["key"] == "Material"
    assert data["value"] == "Aluminium"
    assert data["product_id"] == product["id"]


async def test_add_feature_with_detailed_description(admin_client):
    product = await create_product(admin_client)
    response = await add_feature(admin_client, product["id"], detailed_description="Brushed finish")
    assert response.status_code == 200
    assert response.json()["data"]["detailed_description"] == "Brushed finish"


async def test_add_feature_product_not_found(admin_client):
    response = await add_feature(admin_client, 999999)
    assert response.status_code == 404


async def test_add_feature_duplicate_key_conflicts(admin_client):
    product = await create_product(admin_client)
    await add_feature(admin_client, product["id"], key="Material")
    response = await add_feature(admin_client, product["id"], key="Material")
    assert response.status_code == 500


@pytest.mark.parametrize(
    "overrides",
    [{"key": ""}, {"value": ""}, {}],
    ids=["empty_key", "empty_value", "missing_fields"],
)
async def test_add_feature_invalid(admin_client, overrides):
    product = await create_product(admin_client)
    response = await admin_client.post(f"/products-feature/{product['id']}", json=overrides)
    assert response.status_code == 422


# ── GET /products-feature/{product_id} ───────────────────────────────────────

async def test_fetch_features_success(admin_client):
    product = await create_product(admin_client)
    await add_feature(admin_client, product["id"], key="Material", value="Aluminium")
    await add_feature(admin_client, product["id"], key="Weight", value="1.2kg")

    response = await admin_client.get(f"/products-feature/{product['id']}")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["features"]) == 2
    assert data["images"] == []


async def test_fetch_features_empty(admin_client):
    product = await create_product(admin_client)
    response = await admin_client.get(f"/products-feature/{product['id']}")
    assert response.status_code == 200
    assert response.json()["data"]["features"] == []


# ── PUT /products-feature/{product_id}/{feature_id} ──────────────────────────

async def test_update_feature_success(admin_client):
    product = await create_product(admin_client)
    feature = (await add_feature(admin_client, product["id"], key="Material", value="Aluminium")).json()["data"]

    response = await admin_client.put(
        f"/products-feature/{product['id']}/{feature['id']}",
        json={"key": "Material", "value": "Steel"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["value"] == "Steel"


async def test_update_feature_not_found(admin_client):
    product = await create_product(admin_client)
    response = await admin_client.put(
        f"/products-feature/{product['id']}/999999",
        json={"key": "k", "value": "v"},
    )
    assert response.status_code == 404


async def test_update_feature_wrong_product(admin_client):
    product_a = await create_product(admin_client)
    product_b = await create_product(admin_client)
    feature = (await add_feature(admin_client, product_a["id"])).json()["data"]

    response = await admin_client.put(
        f"/products-feature/{product_b['id']}/{feature['id']}",
        json={"key": "k", "value": "v"},
    )
    assert response.status_code == 404


# ── DELETE /products-feature/{product_id} ────────────────────────────────────

async def test_delete_feature_success(admin_client):
    product = await create_product(admin_client)
    feature = (await add_feature(admin_client, product["id"])).json()["data"]

    response = await admin_client.delete(
        f"/products-feature/{product['id']}", params={"feature_id": feature["id"]}
    )
    assert response.status_code == 200

    features = (await admin_client.get(f"/products-feature/{product['id']}")).json()["data"]["features"]
    assert features == []


async def test_delete_feature_not_found(admin_client):
    product = await create_product(admin_client)
    response = await admin_client.delete(
        f"/products-feature/{product['id']}", params={"feature_id": 999999}
    )
    assert response.status_code == 404


async def test_delete_feature_missing_feature_id(admin_client):
    product = await create_product(admin_client)
    response = await admin_client.delete(f"/products-feature/{product['id']}")
    assert response.status_code == 422
