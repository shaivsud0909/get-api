import uuid

import pytest


async def create_product(admin_client, **overrides):
    payload = {"name": f"Review Widget {uuid.uuid4().hex[:6]}", "price": 10.0, **overrides}
    resp = await admin_client.post("/add-products", json=payload)
    assert resp.status_code == 200, resp.text
    return resp.json()["data"]


async def add_review(user_client, product_id, **overrides):
    payload = {"rating": 5, "comment": "Great product", **overrides}
    return await user_client.post(f"/products/{product_id}/reviews", json=payload)


# ── Auth guard ────────────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "method, url, kwargs",
    [
        ("get", "/products/1/reviews", {}),
        ("post", "/products/1/reviews", {"json": {"rating": 5}}),
        ("get", "/reviews/1", {}),
        ("put", "/reviews/1", {"json": {"rating": 4}}),
        ("delete", "/reviews/1", {}),
    ],
)
async def test_review_routes_require_token(client, method, url, kwargs):
    response = await client.request(method.upper(), url, **kwargs)
    assert response.status_code == 401


@pytest.mark.parametrize(
    "method, url, kwargs",
    [
        ("post", "/products/1/reviews", {"json": {"rating": 5}}),
        ("put", "/reviews/1", {"json": {"rating": 4}}),
    ],
)
async def test_review_routes_reject_admin(admin_client, method, url, kwargs):
    response = await admin_client.request(method.upper(), url, **kwargs)
    assert response.status_code == 403


# ── POST /products/{product_id}/reviews ──────────────────────────────────────

async def test_add_review_success(user_client, admin_client):
    product = await create_product(admin_client)
    response = await add_review(user_client, product["id"], rating=4, comment="Pretty good")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["rating"] == 4
    assert data["comment"] == "Pretty good"
    assert data["product_id"] == product["id"]


async def test_add_review_without_comment(user_client, admin_client):
    product = await create_product(admin_client)
    response = await add_review(user_client, product["id"], rating=3, comment=None)
    assert response.status_code == 200
    assert response.json()["data"]["comment"] is None


@pytest.mark.parametrize(
    "overrides",
    [{"rating": 0}, {"rating": 6}, {}],
    ids=["rating_too_low", "rating_too_high", "missing_rating"],
)
async def test_add_review_invalid_rating(user_client, admin_client, overrides):
    product = await create_product(admin_client)
    payload = {"comment": "x", **overrides}
    response = await user_client.post(f"/products/{product['id']}/reviews", json=payload)
    assert response.status_code == 422


async def test_add_review_comment_too_long(user_client, admin_client):
    product = await create_product(admin_client)
    response = await add_review(user_client, product["id"], comment="x" * 501)
    assert response.status_code == 422


# ── GET /products/{product_id}/reviews ───────────────────────────────────────

async def test_fetch_reviews_for_product(user_client, admin_client, client):
    product = await create_product(admin_client)
    await add_review(user_client, product["id"], rating=5)

    other = {"email": f"other-{uuid.uuid4().hex[:10]}@example.com", "password": "OtherPass123!"}
    await client.post("/signup", json=other)
    other_token = (await client.post("/login", json=other)).json()["access_token"]
    client.headers["Authorization"] = f"Bearer {other_token}"
    await add_review(client, product["id"], rating=2)

    response = await user_client.get(f"/products/{product['id']}/reviews")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 2
    assert {r["rating"] for r in data} == {5, 2}


async def test_add_review_twice_for_same_product_conflicts(user_client, admin_client):
    product = await create_product(admin_client)
    await add_review(user_client, product["id"], rating=5)
    response = await add_review(user_client, product["id"], rating=3)
    assert response.status_code == 500


async def test_fetch_reviews_for_product_with_none(user_client, admin_client):
    product = await create_product(admin_client)
    response = await user_client.get(f"/products/{product['id']}/reviews")
    assert response.status_code == 200
    assert response.json()["data"] == []


# ── GET /reviews/{review_id} ──────────────────────────────────────────────────

async def test_fetch_review_success(user_client, admin_client):
    product = await create_product(admin_client)
    review = (await add_review(user_client, product["id"])).json()["data"]

    response = await user_client.get(f"/reviews/{review['id']}")
    assert response.status_code == 200
    assert response.json()["data"]["id"] == review["id"]


async def test_fetch_review_not_found(user_client):
    response = await user_client.get("/reviews/999999")
    assert response.status_code == 404


# ── PUT /reviews/{review_id} ──────────────────────────────────────────────────

async def test_edit_review_success(user_client, admin_client):
    product = await create_product(admin_client)
    review = (await add_review(user_client, product["id"], rating=3)).json()["data"]

    response = await user_client.put(f"/reviews/{review['id']}", json={"rating": 5, "comment": "Updated"})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["rating"] == 5
    assert data["comment"] == "Updated"


async def test_edit_review_partial_update(user_client, admin_client):
    product = await create_product(admin_client)
    review = (await add_review(user_client, product["id"], rating=3, comment="Original")).json()["data"]

    response = await user_client.put(f"/reviews/{review['id']}", json={"comment": "Only comment changed"})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["rating"] == 3
    assert data["comment"] == "Only comment changed"


async def test_edit_review_not_found(user_client):
    response = await user_client.put("/reviews/999999", json={"rating": 4})
    assert response.status_code == 404


async def test_edit_review_belongs_to_another_user(user_client, admin_client, client):
    product = await create_product(admin_client)
    review = (await add_review(user_client, product["id"])).json()["data"]

    other = {"email": f"other-{uuid.uuid4().hex[:10]}@example.com", "password": "OtherPass123!"}
    await client.post("/signup", json=other)
    other_token = (await client.post("/login", json=other)).json()["access_token"]

    response = await client.put(
        f"/reviews/{review['id']}",
        json={"rating": 1},
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert response.status_code == 404


# ── DELETE /reviews/{review_id} ───────────────────────────────────────────────

async def test_delete_review_success(user_client, admin_client):
    product = await create_product(admin_client)
    review = (await add_review(user_client, product["id"])).json()["data"]

    response = await user_client.delete(f"/reviews/{review['id']}")
    assert response.status_code == 200
    assert (await user_client.get(f"/reviews/{review['id']}")).status_code == 404


async def test_admin_can_read_reviews(user_client, admin_client):
    product = await create_product(admin_client)
    review = (await add_review(user_client, product["id"])).json()["data"]

    assert (await admin_client.get(f"/products/{product['id']}/reviews")).status_code == 200
    assert (await admin_client.get(f"/reviews/{review['id']}")).status_code == 200


async def test_admin_can_delete_any_review(user_client, admin_client):
    product = await create_product(admin_client)
    review = (await add_review(user_client, product["id"])).json()["data"]

    response = await admin_client.delete(f"/reviews/{review['id']}")
    assert response.status_code == 200
    assert (await user_client.get(f"/reviews/{review['id']}")).status_code == 404


async def test_delete_review_not_found(user_client):
    response = await user_client.delete("/reviews/999999")
    assert response.status_code == 404


async def test_delete_review_belongs_to_another_user(user_client, admin_client, client):
    product = await create_product(admin_client)
    review = (await add_review(user_client, product["id"])).json()["data"]

    other = {"email": f"other-{uuid.uuid4().hex[:10]}@example.com", "password": "OtherPass123!"}
    await client.post("/signup", json=other)
    other_token = (await client.post("/login", json=other)).json()["access_token"]

    response = await client.delete(
        f"/reviews/{review['id']}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert response.status_code == 404
