import uuid

import pytest


async def create_product(admin_client, **overrides):
    payload = {"name": f"Order Widget {uuid.uuid4().hex[:6]}", "price": 10.0, "stock": 5, **overrides}
    resp = await admin_client.post("/add-products", json=payload)
    assert resp.status_code == 200, resp.text
    return resp.json()["data"]


async def create_address(user_client, **overrides):
    payload = {
        "full_name": "Jane Doe",
        "phone": "9876543210",
        "line1": "221B Baker Street",
        "city": "London",
        "state": "London",
        "postal_code": "NW16XE",
        "country": "UK",
        **overrides,
    }
    resp = await user_client.post("/addresses", json=payload)
    assert resp.status_code == 200, resp.text
    return resp.json()["data"]


async def add_to_cart(user_client, product_id, quantity):
    resp = await user_client.post("/add-to-cart", json={"product_id": product_id, "quantity": quantity})
    assert resp.status_code == 200, resp.text
    return resp.json()["data"]


async def ready_checkout(user_client, admin_client, quantity=1, stock=5, price=10.0):
    product = await create_product(admin_client, stock=stock, price=price)
    address = await create_address(user_client)
    await add_to_cart(user_client, product["id"], quantity)
    return product, address


# ── Auth guard ────────────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "method, url, kwargs",
    [
        ("post", "/checkout", {"json": {"address_id": 1}}),
        ("get", "/orders", {}),
        ("get", "/orders/1", {}),
    ],
)
async def test_order_routes_require_token(client, method, url, kwargs):
    response = await client.request(method.upper(), url, **kwargs)
    assert response.status_code == 401


@pytest.mark.parametrize(
    "method, url, kwargs",
    [
        ("post", "/checkout", {"json": {"address_id": 1}}),
        ("get", "/orders", {}),
        ("get", "/orders/1", {}),
    ],
)
async def test_order_routes_reject_admin(admin_client, method, url, kwargs):
    response = await admin_client.request(method.upper(), url, **kwargs)
    assert response.status_code == 403


# ── POST /checkout ────────────────────────────────────────────────────────────

async def test_checkout_success(user_client, admin_client):
    product, address = await ready_checkout(user_client, admin_client, quantity=2, stock=5, price=10.0)

    response = await user_client.post("/checkout", json={"address_id": address["id"]})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "pending_payment"
    assert data["total_amount"] == 20.0
    assert data["currency"]
    assert data["shipping_address"]["city"] == "London"
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == product["id"]
    assert data["items"][0]["quantity"] == 2


async def test_checkout_empty_cart(user_client, admin_client):
    address = await create_address(user_client)
    response = await user_client.post("/checkout", json={"address_id": address["id"]})
    assert response.status_code == 400


async def test_checkout_insufficient_stock(user_client, admin_client):
    product = await create_product(admin_client, stock=2)
    address = await create_address(user_client)
    await add_to_cart(user_client, product["id"], 2)

    # stock drops below what's in the cart after the item was added
    await admin_client.patch(f"/products/{product['id']}", json={"stock": 1})

    response = await user_client.post("/checkout", json={"address_id": address["id"]})
    assert response.status_code == 400


async def test_checkout_address_not_found(user_client, admin_client):
    product = await create_product(admin_client)
    await add_to_cart(user_client, product["id"], 1)

    response = await user_client.post("/checkout", json={"address_id": 999999})
    assert response.status_code == 404


async def test_checkout_address_belongs_to_another_user(user_client, admin_client, client):
    product, address = await ready_checkout(user_client, admin_client)

    other = {"email": f"other-{uuid.uuid4().hex[:10]}@example.com", "password": "OtherPass123!"}
    await client.post("/signup", json=other)
    other_token = (await client.post("/login", json=other)).json()["access_token"]

    response = await client.post(
        "/checkout",
        json={"address_id": address["id"]},
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert response.status_code == 404


async def test_checkout_missing_address_id(user_client):
    response = await user_client.post("/checkout", json={})
    assert response.status_code == 422


# ── GET /orders ───────────────────────────────────────────────────────────────

async def test_fetch_orders_empty(user_client):
    response = await user_client.get("/orders")
    assert response.status_code == 200
    assert response.json()["data"] == []


async def test_fetch_orders_lists_own_orders(user_client, admin_client):
    product, address = await ready_checkout(user_client, admin_client)
    order = (await user_client.post("/checkout", json={"address_id": address["id"]})).json()["data"]

    response = await user_client.get("/orders")
    assert response.status_code == 200
    data = response.json()["data"]
    assert any(o["id"] == order["id"] for o in data)


async def test_fetch_orders_does_not_leak_other_users(user_client, admin_client, client):
    await ready_checkout(user_client, admin_client)

    other = {"email": f"other-{uuid.uuid4().hex[:10]}@example.com", "password": "OtherPass123!"}
    await client.post("/signup", json=other)
    other_token = (await client.post("/login", json=other)).json()["access_token"]

    response = await client.get("/orders", headers={"Authorization": f"Bearer {other_token}"})
    assert response.status_code == 200
    assert response.json()["data"] == []


# ── GET /orders/{order_id} ────────────────────────────────────────────────────

async def test_fetch_order_success(user_client, admin_client):
    product, address = await ready_checkout(user_client, admin_client)
    order = (await user_client.post("/checkout", json={"address_id": address["id"]})).json()["data"]

    response = await user_client.get(f"/orders/{order['id']}")
    assert response.status_code == 200
    assert response.json()["data"]["id"] == order["id"]


async def test_fetch_order_not_found(user_client):
    response = await user_client.get("/orders/999999")
    assert response.status_code == 404


async def test_fetch_order_belongs_to_another_user(user_client, admin_client, client):
    product, address = await ready_checkout(user_client, admin_client)
    order = (await user_client.post("/checkout", json={"address_id": address["id"]})).json()["data"]

    other = {"email": f"other-{uuid.uuid4().hex[:10]}@example.com", "password": "OtherPass123!"}
    await client.post("/signup", json=other)
    other_token = (await client.post("/login", json=other)).json()["access_token"]

    response = await client.get(f"/orders/{order['id']}", headers={"Authorization": f"Bearer {other_token}"})
    assert response.status_code == 404
