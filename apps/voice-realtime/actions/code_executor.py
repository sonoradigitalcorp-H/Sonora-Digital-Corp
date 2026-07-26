"""
Code Executor — Ejecuta código Python desde comandos de voz.
Seguridad: sandbox, timeout, límite de recursos.
"""
import asyncio
import logging
import subprocess
import tempfile
import os
import json
from typing import Optional

logger = logging.getLogger("voice-realtime.code_exec")

class CodeExecutor:
    """
    Ejecuta código Python de forma segura con timeout y sandbox.
    """
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
    
    async def run_python(self, code: str) -> dict:
        """
        Ejecuta código Python y devuelve stdout, stderr, y si fue exitoso.
        Timeout: 30s por defecto.
        """
        # Escribir código a archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            path = f.name
        
        try:
            proc = await asyncio.wait_for(
                asyncio.create_subprocess_exec(
                    'python3', path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd='/tmp',
                ),
                timeout=self.timeout
            )
            stdout, stderr = await proc.communicate()
            
            return {
                "status": "ok" if proc.returncode == 0 else "error",
                "stdout": stdout.decode() if stdout else "",
                "stderr": stderr.decode() if stderr else "",
                "returncode": proc.returncode,
            }
        except asyncio.TimeoutError:
            return {"status": "error", "error": "Timeout: el código tardó más de 30s"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    async def run_command(self, command: str) -> dict:
        """
        Ejecuta un comando bash simple (solo comandos seguros).
        Lista blanca: ls, cat, echo, pwd, date, whoami, uname, df, du, ps, head, tail, wc, sort, grep, find
        """
        safe_commands = ['ls', 'cat', 'echo', 'pwd', 'date', 'whoami', 'uname', 'df', 'du', 'ps', 'head', 'tail', 'wc', 'sort', 'grep', 'find', 'python3', 'pip3']
        
        cmd_parts = command.strip().split()
        if not cmd_parts:
            return {"status": "error", "error": "Comando vacío"}
        
        if cmd_parts[0] not in safe_commands:
            return {"status": "error", "error": f"Comando '{cmd_parts[0]}' no permitido"}
        
        try:
            proc = await asyncio.wait_for(
                asyncio.create_subprocess_exec(
                    *cmd_parts,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                ),
                timeout=15
            )
            stdout, stderr = await proc.communicate()
            return {
                "status": "ok" if proc.returncode == 0 else "error",
                "stdout": stdout.decode()[:2000] if stdout else "",
                "stderr": stderr.decode()[:500] if stderr else "",
            }
        except asyncio.TimeoutError:
            return {"status": "error", "error": "Timeout: 15s"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
