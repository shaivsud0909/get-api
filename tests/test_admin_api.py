import pytest


async def create_product(admin_client, **overrides):
    payload = {"name": "Test Product", "price": 1.0, **overrides}
    resp = await admin_client.post("/add-products", json=payload)
    assert resp.status_code == 200, resp.text
    return resp.json()["data"]


# ── Auth guard ────────────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "method, url, kwargs",
    [
        ("get", "/fetch-products", {}),
        ("get", "/products/1", {}),
        ("post", "/add-products", {"json": {"name": "x", "price": 1.0}}),
        ("patch", "/products/1", {"json": {"price": 1.0}}),
        ("delete", "/products/1", {}),
    ],
)
async def test_admin_routes_require_token(client, method, url, kwargs):
    response = await client.request(method.upper(), url, **kwargs)
    assert response.status_code == 401


@pytest.mark.parametrize(
    "method, url, kwargs",
    [
        ("get", "/fetch-products", {}),
        ("get", "/products/1", {}),
        ("post", "/add-products", {"json": {"name": "x", "price": 1.0}}),
        ("patch", "/products/1", {"json": {"price": 1.0}}),
        ("delete", "/products/1", {}),
    ],
)
async def test_admin_routes_reject_user(user_client, method, url, kwargs):
    response = await user_client.request(method.upper(), url, **kwargs)
    assert response.status_code == 403


# ── GET /products/{product_id} ──────────────────────────────────────────────

async def test_fetch_product_success(admin_client):
    product = await create_product(admin_client, name="Fetch Me")
    response = await admin_client.get(f"/products/{product['id']}")
    assert response.status_code == 200


async def test_fetch_product_not_found(admin_client):
    response = await admin_client.get("/products/999999")
    assert response.status_code == 404


# ── GET /fetch-products ──────────────────────────────────────────────────────

async def test_fetch_all_products(admin_client):
    response = await admin_client.get("/fetch-products")
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)


async def test_fetch_products_filter_by_category(admin_client):
    response = await admin_client.get("/fetch-products", params={"category": "Uncategorized"})
    assert response.status_code == 200


@pytest.mark.parametrize("customisable", [True, False])
async def test_fetch_products_filter_customisable(admin_client, customisable):
    response = await admin_client.get("/fetch-products", params={"customisable": customisable})
    assert response.status_code == 200
    assert all(p["customisable"] is customisable for p in response.json()["data"])


async def test_fetch_products_order_by_price_desc(admin_client):
    response = await admin_client.get("/fetch-products", params={"order_by": "price", "order": "desc"})
    assert response.status_code == 200
    prices = [p["price"] for p in response.json()["data"]]
    assert prices == sorted(prices, reverse=True)


async def test_fetch_products_order_by_name_asc(admin_client):
    response = await admin_client.get("/fetch-products", params={"order_by": "name", "order": "asc"})
    assert response.status_code == 200
    names = [p["name"] for p in response.json()["data"]]
    assert names == sorted(names)


async def test_fetch_products_invalid_order_by(admin_client):
    response = await admin_client.get("/fetch-products", params={"order_by": "invalid_field"})
    assert response.status_code == 422


# ── POST /add-products ───────────────────────────────────────────────────────

async def test_add_product_success(admin_client):
    payload = {
        "name": "Test Product",
        "price": 9.99,
        "stock": 10,
        "category": "Testing",
        "description": "A product created during testing",
        "customisable": False,
    }
    response = await admin_client.post("/add-products", json=payload)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["name"] == payload["name"]
    assert data["price"] == payload["price"]


async def test_add_product_minimal_fields(admin_client):
    response = await admin_client.post("/add-products", json={"name": "Minimal Product", "price": 0.0})
    assert response.status_code == 200
    assert response.json()["data"]["stock"] == 0
    assert response.json()["data"]["customisable"] is False


@pytest.mark.parametrize(
    "payload",
    [
        {"price": 5.0},
        {"name": "Bad Price", "price": -1.0},
        {"name": "Bad Stock", "price": 5.0, "stock": -5},
        {"name": "x" * 101, "price": 1.0},
        {"name": "", "price": 1.0},
    ],
    ids=["missing_name", "negative_price", "negative_stock", "name_too_long", "empty_name"],
)
async def test_add_product_invalid(admin_client, payload):
    response = await admin_client.post("/add-products", json=payload)
    assert response.status_code == 422


# ── PATCH /products/{product_id} ─────────────────────────────────────────────

async def test_edit_product_success(admin_client):
    product = await create_product(admin_client, name="Edit Me", price=5.0)
    response = await admin_client.patch(f"/products/{product['id']}", json={"price": 19.99, "stock": 50})
    assert response.status_code == 200
    assert response.json()["data"]["price"] == 19.99
    assert response.json()["data"]["stock"] == 50


async def test_edit_product_not_found(admin_client):
    response = await admin_client.patch("/products/999999", json={"price": 1.0})
    assert response.status_code == 404


async def test_edit_product_no_fields(admin_client):
    product = await create_product(admin_client, name="No Update")
    response = await admin_client.patch(f"/products/{product['id']}", json={})
    assert response.status_code == 400


async def test_edit_product_negative_price(admin_client):
    product = await create_product(admin_client, name="Bad Edit")
    response = await admin_client.patch(f"/products/{product['id']}", json={"price": -5.0})
    assert response.status_code == 422


# ── DELETE /products/{product_id} ────────────────────────────────────────────

async def test_delete_product_success(admin_client):
    product = await create_product(admin_client, name="Delete Me")
    response = await admin_client.delete(f"/products/{product['id']}")
    assert response.status_code == 200
    assert (await admin_client.get(f"/products/{product['id']}")).status_code == 404


async def test_delete_product_not_found(admin_client):
    response = await admin_client.delete("/products/999999")
    assert response.status_code == 404


async def test_delete_product_twice(admin_client):
    product = await create_product(admin_client, name="Delete Twice")
    await admin_client.delete(f"/products/{product['id']}")
    response = await admin_client.delete(f"/products/{product['id']}")
    assert response.status_code == 404
