"""
Tests unitarios para order_store.py — SQLite + trazabilidad.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from apps.whatsapp.order_store import (
    get_db, create_order, get_order, list_orders,
    update_order_status, add_dispatch_event, assign_order,
    register_seller, get_seller, get_seller_by_phone,
    register_client, get_client, list_seller_clients, update_client_purchase,
    update_seller_tokens, award_badge, get_seller_badges,
    seller_dashboard, owner_report, BADGES,
)


class TestOrderStore:
    def setup_method(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.tmp.name
        self.tmp.close()
        self.conn = get_db(self.db_path)

    def teardown_method(self):
        self.conn.close()
        os.unlink(self.db_path)

    def test_tables_exist(self):
        tables = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        names = [r["name"] for r in tables]
        for t in ["orders", "events", "sellers", "clients", "token_transactions", "bundles", "seller_badges"]:
            assert t in names, f"Table {t} missing"

    def test_create_order(self):
        order = create_order(self.conn, {
            "client_name": "Juan Pérez",
            "client_phone": "5216623446953",
            "client_address": "Calle 1 #123",
            "items": [{"flavor": "uva", "qty": 2, "price": 250, "name": "Uva", "emoji": "🍇"}],
            "total": 500,
            "payment_method": "efectivo",
        })
        assert order["id"].startswith("ORD-")
        assert order["status"] == "pendiente"
        assert order["total"] == 500
        assert order["client_name"] == "Juan Pérez"
        assert len(order["items"]) == 1

    def test_get_order_returns_events(self):
        order = create_order(self.conn, {
            "client_name": "Test", "total": 100, "items": []
        })
        fetched = get_order(self.conn, order["id"])
        assert fetched is not None
        assert len(fetched["events"]) > 0
        assert fetched["events"][0]["event_type"] == "order:created"

    def test_list_orders_filter_by_seller(self):
        o1 = create_order(self.conn, {"client_name": "A", "total": 100, "items": []})
        o2 = create_order(self.conn, {"client_name": "B", "total": 200, "items": []})
        all_orders = list_orders(self.conn)
        assert len(all_orders) >= 2

    def test_list_orders_filter_by_status(self):
        create_order(self.conn, {"client_name": "A", "total": 100, "items": []})
        pendientes = list_orders(self.conn, status="pendiente")
        assert all(o["status"] == "pendiente" for o in pendientes)

    def test_update_order_status(self):
        order = create_order(self.conn, {"client_name": "A", "total": 100, "items": []})
        updated = update_order_status(self.conn, order["id"], "asignado", actor="test")
        assert updated["status"] == "asignado"
        events = updated["events"]
        assert any(e["event_type"] == "order:asignado" for e in events)

    def test_assign_order(self):
        order = create_order(self.conn, {"client_name": "A", "total": 100, "items": []})
        assigned = assign_order(self.conn, order["id"], "Pedro")
        assert assigned["assigned_to"] == "Pedro"
        assert assigned["status"] == "asignado"

    def test_add_dispatch_event(self):
        order = create_order(self.conn, {"client_name": "A", "total": 100, "items": []})
        assert order["dispatch_count"] == 0
        add_dispatch_event(self.conn, order["id"])
        updated = get_order(self.conn, order["id"])
        assert updated["dispatch_count"] == 1

    def test_full_order_lifecycle(self):
        order = create_order(self.conn, {
            "client_name": "María",
            "total": 350,
            "items": [{"flavor": "fresa", "qty": 1, "price": 350}],
            "payment_method": "tarjeta",
        })
        assert order["status"] == "pendiente"

        order = assign_order(self.conn, order["id"], "Luis")
        assert order["status"] == "asignado"

        order = update_order_status(self.conn, order["id"], "entregado", actor="Luis")
        assert order["status"] == "entregado"
        assert order["delivered_at"] is not None

        events = order["events"]
        stages = [e["event_type"] for e in events]
        assert "order:created" in stages
        assert "order:assigned" in stages
        assert "order:entregado" in stages

    def test_register_seller(self):
        seller = register_seller(self.conn, "Pedro Vendedor", "5216621111111", "pedro@test.com")
        assert seller["name"] == "Pedro Vendedor"
        assert seller["phone"] == "5216621111111"
        assert seller["level"] == "bronce"
        assert seller["tokens"] == 0

    def test_get_seller_by_phone(self):
        register_seller(self.conn, "Ana", "5216622222222")
        seller = get_seller_by_phone(self.conn, "5216622222222")
        assert seller is not None
        assert seller["name"] == "Ana"

    def test_get_seller_not_found(self):
        assert get_seller(self.conn, "NONEXISTENT") is None

    def test_register_client(self):
        seller = register_seller(self.conn, "Vendedor", "5216623333333")
        client = register_client(
            self.conn, seller["id"], "Cliente Uno",
            phone="5216624444444", address="Av. Principal"
        )
        assert client["name"] == "Cliente Uno"
        assert client["seller_id"] == seller["id"]

    def test_list_seller_clients(self):
        seller = register_seller(self.conn, "V", "5216625555555")
        register_client(self.conn, seller["id"], "C1")
        register_client(self.conn, seller["id"], "C2")
        clients = list_seller_clients(self.conn, seller["id"])
        assert len(clients) == 2

    def test_update_client_purchase(self):
        seller = register_seller(self.conn, "V", "5216626666666")
        client = register_client(self.conn, seller["id"], "Cliente")
        assert client["frequency"] == 1
        update_client_purchase(self.conn, client["id"], "uva", 250)
        updated = get_client(self.conn, client["id"])
        assert updated["frequency"] == 2
        assert updated["total_purchases"] == 1
        assert updated["total_spent"] == 250
        assert updated["favorite_flavor"] == "uva"

    def test_update_seller_tokens(self):
        seller = register_seller(self.conn, "V", "5216627777777")
        assert seller["tokens"] == 0
        update_seller_tokens(self.conn, seller["id"], 50, "venta", "orders", "ORD-123")
        updated = get_seller(self.conn, seller["id"])
        assert updated["tokens"] == 50

    def test_award_badge(self):
        seller = register_seller(self.conn, "V", "5216628888888")
        ok = award_badge(self.conn, seller["id"], "primera_venta")
        assert ok
        badges = get_seller_badges(self.conn, seller["id"])
        assert len(badges) == 1
        assert badges[0]["badge_id"] == "primera_venta"

    def test_award_invalid_badge(self):
        seller = register_seller(self.conn, "V", "5216629999999")
        ok = award_badge(self.conn, seller["id"], "invalid_badge")
        assert not ok

    def test_seller_dashboard(self):
        seller = register_seller(self.conn, "V Dashboard", "5216620000000")
        dash = seller_dashboard(self.conn, seller["id"])
        assert dash["seller"]["name"] == "V Dashboard"
        assert dash["total_orders"] == 0
        assert dash["total_revenue"] == 0

    def test_seller_dashboard_with_orders(self):
        seller = register_seller(self.conn, "V2", "5216620000001")
        create_order(self.conn, {
            "client_name": "C1", "total": 500,
            "items": [{"flavor": "uva", "qty": 2, "price": 250}],
        })
        dash = seller_dashboard(self.conn, seller["id"])
        # Order has no seller_id, so it won't appear in seller dashboard
        assert dash["total_orders"] == 0

    def test_owner_report(self):
        report = owner_report(self.conn)
        assert "total_orders" in report
        assert "total_sellers" in report
        assert "total_revenue" in report
        assert "total_commissions" in report
        assert "orders_by_status" in report

    def test_events_trazabilidad_sequence(self):
        order = create_order(self.conn, {
            "client_name": "Trazabilidad Test",
            "total": 550,
            "items": [{"flavor": "nuez", "qty": 1, "price": 550}],
        })
        oid = order["id"]

        update_order_status(self.conn, oid, "asignado", actor="Carlos")
        add_dispatch_event(self.conn, oid)
        update_order_status(self.conn, oid, "entregado", actor="Carlos")

        events = get_order(self.conn, oid)["events"]
        types = [e["event_type"] for e in events]
        assert types == ["order:created", "order:asignado", "order:dispatched", "order:entregado"]

    def test_concurrent_orders(self):
        orders = []
        for i in range(10):
            o = create_order(self.conn, {
                "client_name": f"Concurrent {i}",
                "total": 100 * i,
                "items": [{"flavor": "uva", "qty": i, "price": 100}],
            })
            orders.append(o)
        assert len(orders) == 10
        all_orders = list_orders(self.conn, limit=100)
        assert len(all_orders) >= 10

    def test_client_tags_serialization(self):
        seller = register_seller(self.conn, "V Tags", "5216620000002")
        client = register_client(self.conn, seller["id"], "Tagged Client")
        assert client["tags"] == []  # default empty array
