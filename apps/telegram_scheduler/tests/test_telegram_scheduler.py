"""Tests for Telegram Scheduler — db, whatsapp, handlers, scheduler."""

import os
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure the module path is set
_HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_HERE))

os.environ["TELEGRAM_TOKEN"] = "test:token"
os.environ["OWNER_TELEGRAM_ID"] = "12345"


class TestDB(unittest.TestCase):
    """Tests for the database layer."""

    def setUp(self):
        import db
        self.db = db
        self.db.DB_PATH = Path(_HERE) / "test_telegram_scheduler.db"
        if self.db.DB_PATH.exists() or Path(str(self.db.DB_PATH) + "-wal").exists():
            self.db.DB_PATH.unlink(missing_ok=True)
            Path(str(self.db.DB_PATH) + "-wal").unlink(missing_ok=True)
            Path(str(self.db.DB_PATH) + "-shm").unlink(missing_ok=True)
        self.db.init_db()

    def tearDown(self):
        import db
        if db.DB_PATH.exists() or Path(str(db.DB_PATH) + "-wal").exists():
            db.DB_PATH.unlink(missing_ok=True)
            Path(str(db.DB_PATH) + "-wal").unlink(missing_ok=True)
            Path(str(db.DB_PATH) + "-shm").unlink(missing_ok=True)

    def test_add_and_get_cliente(self):
        cid = self.db.add_cliente("Juan Pérez", "123456789", None)
        self.assertIsInstance(cid, int)
        cliente = self.db.get_cliente("Juan Pérez")
        self.assertIsNotNone(cliente)
        self.assertEqual(cliente["nombre"], "Juan Pérez")
        self.assertEqual(cliente["telegram_id"], "123456789")
        self.assertIsNone(cliente["whatsapp_jid"])

    def test_add_duplicate_cliente_raises(self):
        self.db.add_cliente("Test", None, None)
        with self.assertRaises(ValueError):
            self.db.add_cliente("Test", None, None)

    def test_list_clientes(self):
        self.db.add_cliente("A", "1", None)
        self.db.add_cliente("B", None, "b@wa.net")
        lista = self.db.list_clientes()
        self.assertEqual(len(lista), 2)

    def test_delete_cliente(self):
        self.db.add_cliente("Eliminar", None, None)
        ok = self.db.delete_cliente("Eliminar")
        self.assertTrue(ok)
        self.assertIsNone(self.db.get_cliente("Eliminar"))

    def test_delete_nonexistent(self):
        ok = self.db.delete_cliente("NoExiste")
        self.assertFalse(ok)

    def test_mensaje_crud(self):
        cid = self.db.add_cliente("Cliente Msg", None, None)
        futuro = (datetime.now() + timedelta(hours=1)).isoformat()
        mid = self.db.add_mensaje(cid, "Hola cliente", futuro)
        pendientes = self.db.get_pendientes()
        self.assertEqual(len(pendientes), 1)
        self.assertEqual(pendientes[0]["id"], mid)
        self.assertEqual(pendientes[0]["contenido"], "Hola cliente")

        self.db.update_mensaje_estado(mid, "enviado", enviado_en=datetime.now().isoformat())
        pendientes = self.db.get_pendientes()
        self.assertEqual(len(pendientes), 0)

    def test_cancel_mensaje(self):
        cid = self.db.add_cliente("Cancel Test", None, None)
        futuro = (datetime.now() + timedelta(hours=1)).isoformat()
        mid = self.db.add_mensaje(cid, "Test cancel", futuro)
        ok = self.db.cancel_mensaje(mid)
        self.assertTrue(ok)
        msg = self.db.get_mensaje(mid)
        self.assertEqual(msg["estado"], "cancelado")
        # Second cancel should fail
        ok = self.db.cancel_mensaje(mid)
        self.assertFalse(ok)

    def test_historial(self):
        cid = self.db.add_cliente("Hist Test", None, None)
        self.db.add_historial(cid, "Msg 1", "telegram", "enviado", sent_at=datetime.now().isoformat())
        self.db.add_historial(cid, "Msg 2", "whatsapp", "fallido", sent_at=datetime.now().isoformat(), error_msg="error")
        historial = self.db.get_historial(cid)
        self.assertEqual(len(historial), 2)
        self.assertEqual(historial[0]["contenido"], "Msg 2")  # DESC order


class TestWhatsApp(unittest.TestCase):
    """Tests for the WhatsApp sender wrapper."""

    @patch("subprocess.run")
    def test_send_whatsapp_success(self, mock_run):
        import whatsapp as wa
        mock_run.return_value = MagicMock(returncode=0, stdout="ok", stderr="")
        success, msg = wa.send_whatsapp("5216623538272", "Hola")
        self.assertTrue(success)

    @patch("subprocess.run")
    def test_send_whatsapp_failure(self, mock_run):
        import whatsapp as wa
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")
        success, msg = wa.send_whatsapp("test@wa.net", "Hola")
        self.assertFalse(success)

    @patch("subprocess.run", side_effect=TimeoutError("timeout"))
    def test_send_whatsapp_timeout(self, mock_run):
        import whatsapp as wa
        success, msg = wa.send_whatsapp("test@wa.net", "Hola")
        self.assertFalse(success)

    def test_send_whatsapp_jid_normalization(self):
        import whatsapp as wa
        # Test that JID without domain gets normalized
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="ok", stderr="")
            wa.send_whatsapp("5216623538272", "Hola")
            args = mock_run.call_args[0][0]
            to_idx = args.index("--to")
            self.assertIn("@s.whatsapp.net", args[to_idx + 1])

    def test_send_whatsapp_jid_already_normalized(self):
        import whatsapp as wa
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="ok", stderr="")
            wa.send_whatsapp("test@s.whatsapp.net", "Hola")
            args = mock_run.call_args[0][0]
            to_idx = args.index("--to")
            self.assertEqual(args[to_idx + 1], "test@s.whatsapp.net")


class TestHandlers(unittest.TestCase):
    """Tests for command handlers."""

    def setUp(self):
        self.update = MagicMock()
        self.context = MagicMock()
        self.update.effective_user.id = 12345

    def test_is_owner_match(self):
        from handlers import _is_owner
        self.assertTrue(_is_owner(self.update))

    def test_is_owner_no_match(self):
        from handlers import _is_owner
        self.update.effective_user.id = 99999
        self.assertFalse(_is_owner(self.update))


class TestScheduler(unittest.TestCase):
    """Tests for the scheduler logic."""

    def test_start_scheduler_creates_task(self):
        import asyncio
        import scheduler
        app = MagicMock()

        async def _run():
            task = scheduler.start_scheduler(app)
            self.assertIsInstance(task, asyncio.Task)
            task.cancel()

        asyncio.run(_run())


if __name__ == "__main__":
    unittest.main()
