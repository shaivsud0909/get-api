import uuid

import pytest


@pytest.fixture
async def product(admin_client):
    resp = await admin_client.post(
        "/add-products",
        json={"name": f"Cart Widget {uuid.uuid4().hex[:6]}", "price": 25.0, "stock": 10},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["data"]


async def add_to_cart(user_client, product_id, quantity):
    return await user_client.post(
        "/add-to-cart",
        json={"product_id": product_id, "quantity": quantity},
        params={"user_id": user_client.user_id},
    )


# ── Auth guard ────────────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "method, url, kwargs",
    [
        ("get", "/products", {}),
        ("get", "/customisable-products", {}),
        ("get", "/cart", {"params": {"user_id": 1}}),
        ("post", "/add-to-cart", {"json": {"product_id": 1, "quantity": 1}, "params": {"user_id": 1}}),
        ("patch", "/cart-item/1", {"json": {"quantity": 1}, "params": {"user_id": 1}}),
    ],
)
async def test_user_routes_require_token(client, method, url, kwargs):
    response = await client.request(method.upper(), url, **kwargs)
    assert response.status_code == 401


@pytest.mark.parametrize(
    "method, url, kwargs",
    [
        ("get", "/products", {}),
        ("get", "/customisable-products", {}),
        ("get", "/cart", {"params": {"user_id": 1}}),
        ("post", "/add-to-cart", {"json": {"product_id": 1, "quantity": 1}, "params": {"user_id": 1}}),
        ("patch", "/cart-item/1", {"json": {"quantity": 1}, "params": {"user_id": 1}}),
    ],
)
async def test_user_routes_reject_admin(admin_client, method, url, kwargs):
    response = await admin_client.request(method.upper(), url, **kwargs)
    assert response.status_code == 403


# ── GET /products ─────────────────────────────────────────────────────────────

async def test_fetch_all_products(user_client):
    response = await user_client.get("/products")
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)


async def test_fetch_products_filter_by_category(user_client):
    response = await user_client.get("/products", params={"category": "Uncategorized"})
    assert response.status_code == 200


@pytest.mark.parametrize("customisable", [True, False])
async def test_fetch_products_filter_customisable(user_client, customisable):
    response = await user_client.get("/products", params={"customisable": customisable})
    assert response.status_code == 200
    assert all(p["customisable"] is customisable for p in response.json()["data"])


async def test_fetch_products_order_by_price_desc(user_client):
    response = await user_client.get("/products", params={"order_by": "price", "order": "desc"})
    assert response.status_code == 200
    prices = [p["price"] for p in response.json()["data"]]
    assert prices == sorted(prices, reverse=True)


async def test_fetch_products_order_by_name_asc(user_client):
    response = await user_client.get("/products", params={"order_by": "name", "order": "asc"})
    assert response.status_code == 200
    names = [p["name"] for p in response.json()["data"]]
    assert names == sorted(names)


async def test_fetch_products_invalid_order_by(user_client):
    response = await user_client.get("/products", params={"order_by": "invalid_field"})
    assert response.status_code == 422


# ── GET /customisable-products ───────────────────────────────────────────────

async def test_fetch_customisable_products(user_client):
    response = await user_client.get("/customisable-products")
    assert response.status_code == 200
    assert all(p["customisable"] is True for p in response.json()["data"])


async def test_fetch_customisable_products_filter_by_category(user_client):
    response = await user_client.get("/customisable-products", params={"category": "Uncategorized"})
    assert response.status_code == 200


# ── GET /cart ─────────────────────────────────────────────────────────────────

async def test_create_cart_success(user_client):
    response = await user_client.get("/cart", params={"user_id": user_client.user_id})
    assert response.status_code == 200
    assert response.json()["data"]["user_id"] == user_client.user_id


async def test_create_cart_missing_user_id(user_client):
    response = await user_client.get("/cart")
    assert response.status_code == 422


# ── POST /add-to-cart ─────────────────────────────────────────────────────────

async def test_add_to_cart_success(user_client, product):
    response = await add_to_cart(user_client, product["id"], 2)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["product_id"] == product["id"]
    assert data["quantity"] == 2


async def test_add_to_cart_existing_item_increments_quantity(user_client, product):
    await add_to_cart(user_client, product["id"], 2)
    response = await add_to_cart(user_client, product["id"], 3)
    assert response.status_code == 200
    assert response.json()["data"]["quantity"] == 5


async def test_add_to_cart_product_not_found(user_client):
    response = await add_to_cart(user_client, 999999, 1)
    assert response.status_code == 404


async def test_add_to_cart_insufficient_stock(user_client, product):
    response = await add_to_cart(user_client, product["id"], product["stock"] + 1)
    assert response.status_code == 400


async def test_add_to_cart_increment_exceeds_stock(user_client, product):
    await add_to_cart(user_client, product["id"], product["stock"] - 1)
    response = await add_to_cart(user_client, product["id"], 2)
    assert response.status_code == 400


async def test_add_to_cart_missing_quantity(user_client, product):
    response = await user_client.post(
        "/add-to-cart", json={"product_id": product["id"]}, params={"user_id": user_client.user_id}
    )
    assert response.status_code == 422


async def test_add_to_cart_missing_product_id(user_client):
    response = await user_client.post(
        "/add-to-cart", json={"quantity": 1}, params={"user_id": user_client.user_id}
    )
    assert response.status_code == 422


async def test_add_to_cart_missing_user_id(user_client, product):
    response = await user_client.post("/add-to-cart", json={"product_id": product["id"], "quantity": 1})
    assert response.status_code == 422


# ── PATCH /cart-item/{item_id} ───────────────────────────────────────────────

async def test_edit_cart_item_success(user_client, product):
    item_id = (await add_to_cart(user_client, product["id"], 1)).json()["data"]["id"]
    response = await user_client.patch(
        f"/cart-item/{item_id}", json={"quantity": 4}, params={"user_id": user_client.user_id}
    )
    assert response.status_code == 200
    assert response.json()["data"]["quantity"] == 4


async def test_edit_cart_item_not_found(user_client):
    response = await user_client.patch(
        "/cart-item/999999", json={"quantity": 1}, params={"user_id": user_client.user_id}
    )
    assert response.status_code == 404


async def test_edit_cart_item_insufficient_stock(user_client, product):
    item_id = (await add_to_cart(user_client, product["id"], 1)).json()["data"]["id"]
    response = await user_client.patch(
        f"/cart-item/{item_id}",
        json={"quantity": product["stock"] + 1},
        params={"user_id": user_client.user_id},
    )
    assert response.status_code == 400


async def test_edit_cart_item_invalid_quantity_zero(user_client, product):
    item_id = (await add_to_cart(user_client, product["id"], 1)).json()["data"]["id"]
    response = await user_client.patch(
        f"/cart-item/{item_id}", json={"quantity": 0}, params={"user_id": user_client.user_id}
    )
    assert response.status_code == 422


async def test_edit_cart_item_belongs_to_another_user(user_client, product, client):
    item_id = (await add_to_cart(user_client, product["id"], 1)).json()["data"]["id"]

    other = {"email": f"other-{uuid.uuid4().hex[:10]}@example.com", "password": "OtherPass123!"}
    other_id = (await client.post("/signup", json=other)).json()["id"]
    other_token = (await client.post("/login", json=other)).json()["access_token"]

    response = await client.patch(
        f"/cart-item/{item_id}",
        json={"quantity": 2},
        params={"user_id": other_id},
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert response.status_code == 404
