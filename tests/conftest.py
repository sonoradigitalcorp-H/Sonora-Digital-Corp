"""Global test configuration — ensures test env vars before any imports."""
import os

# Force test mode for Mercado Pago (prevents real API calls)
os.environ["MERCADO_PAGO_ACCESS_TOKEN"] = "TEST-fake"
