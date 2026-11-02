import pytest
from core.logs import logger


# ── GET /products/{product_id} ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_fetch_product_success(client):
    response = await client.get("/products/2")
    logger.info(response.json())
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_fetch_product_not_found(client):
    response = await client.get("/products/999999")
    logger.info(response.json())
    assert response.status_code == 404


# ── GET /fetch-products ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_fetch_all_products(client):
    response = await client.get("/fetch-products")
    logger.info(response.json())
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)


@pytest.mark.asyncio
async def test_fetch_products_filter_by_category(client):
    response = await client.get("/fetch-products", params={"category": "Uncategorized"})
    logger.info(response.json())
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_fetch_products_filter_customisable_true(client):
    response = await client.get("/fetch-products", params={"customisable": True})
    logger.info(response.json())
    assert response.status_code == 200
    data = response.json()["data"]
    assert all(p["customisable"] is True for p in data)


@pytest.mark.asyncio
async def test_fetch_products_filter_customisable_false(client):
    response = await client.get("/fetch-products", params={"customisable": False})
    logger.info(response.json())
    assert response.status_code == 200
    data = response.json()["data"]
    assert all(p["customisable"] is False for p in data)


@pytest.mark.asyncio
async def test_fetch_products_order_by_price_desc(client):
    response = await client.get("/fetch-products", params={"order_by": "price", "order": "desc"})
    logger.info(response.json())
    assert response.status_code == 200
    data = response.json()["data"]
    prices = [p["price"] for p in data]
    assert prices == sorted(prices, reverse=True)


@pytest.mark.asyncio
async def test_fetch_products_order_by_name_asc(client):
    response = await client.get("/fetch-products", params={"order_by": "name", "order": "asc"})
    logger.info(response.json())
    assert response.status_code == 200
    data = response.json()["data"]
    names = [p["name"] for p in data]
    assert names == sorted(names)


@pytest.mark.asyncio
async def test_fetch_products_invalid_order_by(client):
    response = await client.get("/fetch-products", params={"order_by": "invalid_field"})
    logger.info(response.json())
    assert response.status_code == 422


# ── GET /customisable-products ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_fetch_customisable_products(client):
    response = await client.get("/customisable-products")
    logger.info(response.json())
    assert response.status_code == 200
    data = response.json()["data"]
    assert all(p["customisable"] is True for p in data)


@pytest.mark.asyncio
async def test_fetch_customisable_products_filter_by_category(client):
    response = await client.get("/customisable-products", params={"category": "Uncategorized"})
    logger.info(response.json())
    assert response.status_code == 200


# ── POST /add-products ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_add_product_success(client):
    payload = {
        "name": "Test Product",
        "price": 9.99,
        "stock": 10,
        "category": "Testing",
        "description": "A product created during testing",
        "customisable": False,
    }
    response = await client.post("/add-products", json=payload)
    logger.info(response.json())
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["name"] == payload["name"]
    assert data["price"] == payload["price"]


@pytest.mark.asyncio
async def test_add_product_minimal_fields(client):
    payload = {"name": "Minimal Product", "price": 0.0}
    response = await client.post("/add-products", json=payload)
    logger.info(response.json())
    assert response.status_code == 200
    assert response.json()["data"]["stock"] == 0
    assert response.json()["data"]["customisable"] is False


@pytest.mark.asyncio
async def test_add_product_missing_name(client):
    payload = {"price": 5.0}
    response = await client.post("/add-products", json=payload)
    logger.info(response.json())
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_add_product_negative_price(client):
    payload = {"name": "Bad Price", "price": -1.0}
    response = await client.post("/add-products", json=payload)
    logger.info(response.json())
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_add_product_negative_stock(client):
    payload = {"name": "Bad Stock", "price": 5.0, "stock": -5}
    response = await client.post("/add-products", json=payload)
    logger.info(response.json())
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_add_product_name_too_long(client):
    payload = {"name": "x" * 101, "price": 1.0}
    response = await client.post("/add-products", json=payload)
    logger.info(response.json())
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_add_product_empty_name(client):
    payload = {"name": "", "price": 1.0}
    response = await client.post("/add-products", json=payload)
    logger.info(response.json())
    assert response.status_code == 422


# ── PUT /products/{product_id} ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_edit_product_success(client):
    # create a product to update
    create_resp = await client.post("/add-products", json={"name": "Edit Me", "price": 5.0})
    product_id = create_resp.json()["data"]["id"]

    response = await client.put(f"/products/{product_id}", json={"price": 19.99, "stock": 50})
    logger.info(response.json())
    assert response.status_code == 200
    assert response.json()["data"]["price"] == 19.99
    assert response.json()["data"]["stock"] == 50


@pytest.mark.asyncio
async def test_edit_product_not_found(client):
    response = await client.put("/products/999999", json={"price": 1.0})
    logger.info(response.json())
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_edit_product_no_fields(client):
    create_resp = await client.post("/add-products", json={"name": "No Update", "price": 1.0})
    product_id = create_resp.json()["data"]["id"]

    response = await client.put(f"/products/{product_id}", json={})
    logger.info(response.json())
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_edit_product_negative_price(client):
    create_resp = await client.post("/add-products", json={"name": "Bad Edit", "price": 1.0})
    product_id = create_resp.json()["data"]["id"]

    response = await client.put(f"/products/{product_id}", json={"price": -5.0})
    logger.info(response.json())
    assert response.status_code == 422


# ── DELETE /products/{product_id} ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_product_success(client):
    create_resp = await client.post("/add-products", json={"name": "Delete Me", "price": 1.0})
    product_id = create_resp.json()["data"]["id"]

    response = await client.delete(f"/products/{product_id}")
    logger.info(response.json())
    assert response.status_code == 200

    # verify it's gone
    fetch_resp = await client.get(f"/products/{product_id}")
    assert fetch_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_product_not_found(client):
    response = await client.delete("/products/999999")
    logger.info(response.json())
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_product_twice(client):
    create_resp = await client.post("/add-products", json={"name": "Delete Twice", "price": 1.0})
    product_id = create_resp.json()["data"]["id"]

    await client.delete(f"/products/{product_id}")
    response = await client.delete(f"/products/{product_id}")
    logger.info(response.json())
    assert response.status_code == 404
