#!/usr/bin/env python3
"""test_tubandera_flow.py — Unit test para el flujo de clasificación y notificación de Tu Bandera A.C."""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import tubandera_scoring


def test_classification():
    print("🧪 Probando clasificación de perfiles y urgencia de Tu Bandera A.C....")
    
    # 1. Caso Familiar + Urgente
    msg1 = "Necesito ayuda urgente para mi hijo, se encuentra mal y queremos saber si pueden ir por el hoy mismo"
    perfil1 = tubandera_scoring.classify_user_profile(msg1)
    eval1 = tubandera_scoring.evaluate_urgency(msg1)
    
    assert perfil1 == "FAMILIAR", f"Esperado FAMILIAR, obtenido {perfil1}"
    assert eval1["urgencia"] == "ATENCION_INMEDIATA", f"Esperado ATENCION_INMEDIATA, obtenido {eval1['urgencia']}"
    assert eval1["requiere_traslado"] is True, "Esperado requiere_traslado True"
    print("  ✓ Test 1 Passed: Familiar con solicitud de traslado urgente.")

    # 2. Caso Institución
    msg2 = "Buenas tardes, somos una escuela preparatoria y requerimos pláticas sobre prevención de adicciones para nuestros alumnos"
    perfil2 = tubandera_scoring.classify_user_profile(msg2)
    eval2 = tubandera_scoring.evaluate_urgency(msg2)
    
    assert perfil2 == "INSTITUCION", f"Esperado INSTITUCION, obtenido {perfil2}"
    assert eval2["urgencia"] == "MODERADA", f"Esperado MODERADA, obtenido {eval2['urgencia']}"
    print("  ✓ Test 2 Passed: Institución solicitando pláticas de prevención.")

    # 3. Formateo de notificación a Roberto Lara
    notif = tubandera_scoring.format_roberto_notification(
        full_name="Carlos Mendoza",
        phone_or_user="6621234567",
        perfil=perfil1,
        urgencia=eval1["urgencia"],
        servicio_requerido="Traslado y atención en crisis",
        mensaje_original=msg1
    )
    assert "Roberto Lara" not in notif  # el texto es para Roberto
    assert "Carlos Mendoza" in notif
    assert "ATENCION_INMEDIATA" in notif
    print("  ✓ Test 3 Passed: Formateo de notificación WhatsApp listo.")

    print("\n✅ TODOS LOS TESTS DE CLASIFICACIÓN Y DIAGNÓSTICO PASARON (100% PASS).")


if __name__ == "__main__":
    test_classification()
