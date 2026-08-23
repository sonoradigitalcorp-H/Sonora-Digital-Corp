#!/usr/bin/env python3
"""test_fal_webhook.py — Test de integración para el sistema receptor fal.ai"""

import os
import sys
import json
import sqlite3
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import fal_webhook_receiver


def test_receiver():
    print("🧪 Probando inicialización de Base de Datos y procesamiento de Webhook...")
    fal_webhook_receiver.init_db()
    
    # Payload simulado de fal.ai
    mock_payload = {
        "request_id": "test_req_998877",
        "status": "COMPLETED",
        "model": "fal-ai/flux/dev",
        "payload": {
          "prompt": "Test visual image of modern Hermosillo digital lab",
          "seed": 424242,
          "images": [
            {
              "url": "https://v3.fal.media/files/monkey/sample_test.png",
              "width": 1024,
              "height": 1024
            }
          ]
        }
    }
    
    # Procesar
    fal_webhook_receiver.parse_and_process_payload(mock_payload)
    
    # Verificar en SQLite
    conn = sqlite3.connect(fal_webhook_receiver.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT request_id, prompt, model, media_type, status FROM fal_creations WHERE request_id = 'test_req_998877'")
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None, "Error: El registro no fue encontrado en la base de datos"
    assert row[0] == "test_req_998877"
    assert "Hermosillo" in row[1]
    assert row[2] == "fal-ai/flux/dev"
    assert row[3] == "image"
    
    print("✅ TEST PASS: Webhook procesado y registrado correctamente en DB SQLite.")


if __name__ == "__main__":
    test_receiver()
