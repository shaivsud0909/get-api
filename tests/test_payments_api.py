import uuid
from unittest.mock import patch

import pytest


async def create_product(admin_client, **overrides):
    payload = {"name": f"Payment Widget {uuid.uuid4().hex[:6]}", "price": 10.0, "stock": 5, **overrides}
    resp = await admin_client.post("/add-products", json=payload)
    assert resp.status_code == 200, resp.text
    return resp.json()["data"]


async def create_order(user_client, admin_client, quantity=1, stock=5, price=10.0):
    product = await create_product(admin_client, stock=stock, price=price)

    address_payload = {
        "full_name": "Jane Doe",
        "phone": "9876543210",
        "line1": "221B Baker Street",
        "city": "London",
        "state": "London",
        "postal_code": "NW16XE",
        "country": "UK",
    }
    address = (await user_client.post("/addresses", json=address_payload)).json()["data"]

    cart_item = (
        await user_client.post("/add-to-cart", json={"product_id": product["id"], "quantity": quantity})
    ).json()["data"]
    order = (await user_client.post("/checkout", json={"address_id": address["id"]})).json()["data"]
    return product, order, cart_item["id"]


def mock_gateway_order(gateway_order_id=None):
    return patch(
        "app.payments.service.create_gateway_order",
        return_value={"id": gateway_order_id or f"order_{uuid.uuid4().hex[:12]}"},
    )


# ── Auth guard ────────────────────────────────────────────────────────────────

async def test_payment_routes_require_token(client):
    response = await client.post("/payments/initiate", json={"order_id": 1})
    assert response.status_code == 401


async def test_payment_routes_reject_admin(admin_client):
    response = await admin_client.post("/payments/initiate", json={"order_id": 1})
    assert response.status_code == 403


# ── POST /payments/initiate ──────────────────────────────────────────────────

async def test_initiate_payment_success(user_client, admin_client):
    _, order, _ = await create_order(user_client, admin_client, quantity=1, price=10.0)
    gateway_order_id = f"order_{uuid.uuid4().hex[:12]}"

    with mock_gateway_order(gateway_order_id):
        response = await user_client.post("/payments/initiate", json={"order_id": order["id"]})

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["order_id"] == order["id"]
    assert data["gateway_order_id"] == gateway_order_id
    assert data["amount"] == 1000  # paise
    assert data["gateway"] == "razorpay"


async def test_initiate_payment_order_not_found(user_client):
    with mock_gateway_order():
        response = await user_client.post("/payments/initiate", json={"order_id": 999999})
    assert response.status_code == 404


async def test_initiate_payment_order_belongs_to_another_user(user_client, admin_client, client):
    _, order, _ = await create_order(user_client, admin_client)

    other = {"email": f"other-{uuid.uuid4().hex[:10]}@example.com", "password": "OtherPass123!"}
    await client.post("/signup", json=other)
    other_token = (await client.post("/login", json=other)).json()["access_token"]

    with mock_gateway_order():
        response = await client.post(
            "/payments/initiate",
            json={"order_id": order["id"]},
            headers={"Authorization": f"Bearer {other_token}"},
        )
    assert response.status_code == 404


async def test_initiate_payment_order_not_pending(user_client, admin_client):
    _, order, _ = await create_order(user_client, admin_client)

    with mock_gateway_order():
        first = await user_client.post("/payments/initiate", json={"order_id": order["id"]})
    assert first.status_code == 200

    with patch("app.payments.service.verify_webhook_signature", return_value=True):
        payment = first.json()["data"]
        webhook_payload = {
            "event": "payment.captured",
            "payload": {
                "payment": {
                    "entity": {
                        "id": "pay_once",
                        "order_id": payment["gateway_order_id"],
                        "amount": payment["amount"],
                        "currency": payment["currency"],
                    }
                }
            },
        }
        webhook_response = await user_client.post(
            "/payments/webhook",
            json=webhook_payload,
            headers={"X-Razorpay-Signature": "sig"},
        )
    assert webhook_response.status_code == 200

    with mock_gateway_order():
        response = await user_client.post("/payments/initiate", json={"order_id": order["id"]})
    assert response.status_code == 400


async def test_initiate_payment_reuses_existing_unpaid_payment(user_client, admin_client):
    _, order, _ = await create_order(user_client, admin_client)

    with mock_gateway_order():
        first = await user_client.post("/payments/initiate", json={"order_id": order["id"]})
        second = await user_client.post("/payments/initiate", json={"order_id": order["id"]})

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["data"]["payment_id"] == second.json()["data"]["payment_id"]


async def test_initiate_payment_missing_order_id(user_client):
    response = await user_client.post("/payments/initiate", json={})
    assert response.status_code == 422


# ── POST /payments/webhook ────────────────────────────────────────────────────

async def _initiate(user_client, admin_client, **order_kwargs):
    _, order, _ = await create_order(user_client, admin_client, **order_kwargs)
    with mock_gateway_order():
        resp = await user_client.post("/payments/initiate", json={"order_id": order["id"]})
    assert resp.status_code == 200, resp.text
    return order, resp.json()["data"]


def _webhook_payload(event, gateway_order_id, amount, currency, payment_id="pay_x"):
    return {
        "event": event,
        "payload": {
            "payment": {
                "entity": {
                    "id": payment_id,
                    "order_id": gateway_order_id,
                    "amount": amount,
                    "currency": currency,
                }
            }
        },
    }


async def test_webhook_invalid_signature(user_client, admin_client, client):
    order, payment = await _initiate(user_client, admin_client)

    with patch("app.payments.service.verify_webhook_signature", return_value=False):
        response = await client.post(
            "/payments/webhook",
            json=_webhook_payload(
                "payment.captured", payment["gateway_order_id"], payment["amount"], payment["currency"]
            ),
            headers={"X-Razorpay-Signature": "bad"},
        )
    assert response.status_code == 400


async def test_webhook_unknown_event_type(client):
    with patch("app.payments.service.verify_webhook_signature", return_value=True):
        response = await client.post(
            "/payments/webhook",
            json={"event": "some.other.event", "payload": {}},
            headers={"X-Razorpay-Signature": "sig"},
        )
    assert response.status_code == 200
    assert response.json()["data"]["handled"] is False


async def test_webhook_unknown_gateway_order(client):
    with patch("app.payments.service.verify_webhook_signature", return_value=True):
        response = await client.post(
            "/payments/webhook",
            json=_webhook_payload("payment.captured", "order_does_not_exist", 1000, "INR"),
            headers={"X-Razorpay-Signature": "sig"},
        )
    assert response.status_code == 200
    assert response.json()["data"]["handled"] is False


async def test_webhook_amount_mismatch(user_client, admin_client, client):
    order, payment = await _initiate(user_client, admin_client)

    with patch("app.payments.service.verify_webhook_signature", return_value=True):
        response = await client.post(
            "/payments/webhook",
            json=_webhook_payload(
                "payment.captured", payment["gateway_order_id"], payment["amount"] + 1, payment["currency"]
            ),
            headers={"X-Razorpay-Signature": "sig"},
        )
    assert response.status_code == 400


async def test_webhook_payment_captured_confirms_order_and_decrements_stock(user_client, admin_client, client):
    product, order, cart_item_id = await create_order(user_client, admin_client, quantity=2, stock=5, price=10.0)
    with mock_gateway_order():
        payment = (await user_client.post("/payments/initiate", json={"order_id": order["id"]})).json()["data"]

    with patch("app.payments.service.verify_webhook_signature", return_value=True):
        response = await client.post(
            "/payments/webhook",
            json=_webhook_payload(
                "payment.captured", payment["gateway_order_id"], payment["amount"], payment["currency"]
            ),
            headers={"X-Razorpay-Signature": "sig"},
        )
    assert response.status_code == 200
    assert response.json()["data"]["handled"] is True

    order_after = (await user_client.get(f"/orders/{order['id']}")).json()["data"]
    assert order_after["status"] == "confirmed"

    # the fulfilled cart item was deleted
    assert (await user_client.patch(f"/cart-item/{cart_item_id}", json={"quantity": 1})).status_code == 404

    products = (await admin_client.get("/fetch-products")).json()["data"]
    assert next(p for p in products if p["id"] == product["id"])["stock"] == 3


async def test_webhook_duplicate_payment_is_noop(user_client, admin_client, client):
    _, order, _ = await create_order(user_client, admin_client)
    with mock_gateway_order():
        payment = (await user_client.post("/payments/initiate", json={"order_id": order["id"]})).json()["data"]

    payload = _webhook_payload(
        "payment.captured", payment["gateway_order_id"], payment["amount"], payment["currency"]
    )

    with patch("app.payments.service.verify_webhook_signature", return_value=True):
        first = await client.post("/payments/webhook", json=payload, headers={"X-Razorpay-Signature": "sig"})
        second = await client.post("/payments/webhook", json=payload, headers={"X-Razorpay-Signature": "sig"})

    assert first.status_code == 200
    assert first.json()["data"] == {"handled": True}
    assert second.status_code == 200
    assert second.json()["data"] == {"handled": True, "duplicate": True}


async def test_webhook_payment_failed_keeps_order_open(user_client, admin_client, client):
    _, order, _ = await create_order(user_client, admin_client)
    with mock_gateway_order():
        payment = (await user_client.post("/payments/initiate", json={"order_id": order["id"]})).json()["data"]

    with patch("app.payments.service.verify_webhook_signature", return_value=True):
        response = await client.post(
            "/payments/webhook",
            json=_webhook_payload(
                "payment.failed", payment["gateway_order_id"], payment["amount"], payment["currency"]
            ),
            headers={"X-Razorpay-Signature": "sig"},
        )
    assert response.status_code == 200
    assert response.json()["data"]["handled"] is True

    order_after = (await user_client.get(f"/orders/{order['id']}")).json()["data"]
    assert order_after["status"] == "pending_payment"
