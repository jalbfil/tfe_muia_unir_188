#!/usr/bin/env python3
"""Gestor interactivo de servicios del DSS 112 CyL.

Uso:
    python scripts/services.py

Controla Ollama, Backend FastAPI y UI Streamlit con un menú de terminal.
Compatible con Windows (CMD/PowerShell/Git Bash) y Linux/macOS.
"""

from __future__ import annotations

import os
import platform
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

# ── Raíz del repositorio ──────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[1]
IS_WINDOWS = platform.system() == "Windows"

# ── Colores ANSI ──────────────────────────────────────────────────────────────
if IS_WINDOWS:
    os.system("color")  # habilita ANSI en CMD/PowerShell modernos

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"
SEP    = "─" * 62


def c(text: str, color: str) -> str:
    return f"{color}{text}{RESET}"


# ── Definición de servicios ───────────────────────────────────────────────────
SERVICES: dict[str, dict] = {
    "ollama": {
        "label": "Ollama LLM",
        "cmd_windows": ["ollama", "serve"],
        "cmd_unix": ["ollama", "serve"],
        "port": 11434,
        "url": "http://localhost:11434",
        "health_path": "/",
        "health_text": "Ollama is running",
        "pid_key": "ollama_pid",
        "proc_key": "ollama_proc",
        "log_file": REPO_ROOT / "artifacts" / "logs" / "ollama.log",
    },
    "backend": {
        "label": "Backend FastAPI",
        "cmd_windows": [
            "uv", "run", "uvicorn",
            "src.backend.api.main:app", "--port", "8000",
        ],
        "cmd_unix": [
            "uv", "run", "uvicorn",
            "src.backend.api.main:app", "--port", "8000",
        ],
        "port": 8000,
        "url": "http://localhost:8000",
        "health_path": "/healthz",
        "health_text": "ok",
        "pid_key": "backend_pid",
        "proc_key": "backend_proc",
        "log_file": REPO_ROOT / "artifacts" / "logs" / "backend.log",
        "kill_marker": "backend.api.main",
    },
    "ui": {
        "label": "Streamlit UI",
        "cmd_windows": [
            "uv", "run", "streamlit", "run",
            "src/ui/app.py", "--server.port", "8501",
        ],
        "cmd_unix": [
            "uv", "run", "streamlit", "run",
            "src/ui/app.py", "--server.port", "8501",
        ],
        "port": 8501,
        "url": "http://localhost:8501",
        "health_path": "/_stcore/health",
        "health_text": "ok",
        "pid_key": "ui_pid",
        "proc_key": "ui_proc",
        "log_file": REPO_ROOT / "artifacts" / "logs" / "ui.log",
        "kill_marker": "ui/app.py",
    },
}

# Procesos arrancados en ESTA sesión del script
_session_procs: dict[str, subprocess.Popen] = {}


# ── Helpers de proceso y red ──────────────────────────────────────────────────

def _get_pid_by_port(port: int) -> int | None:
    """Devuelve el PID que escucha en el puerto, buscando en el OS."""
    try:
        if IS_WINDOWS:
            r = subprocess.run(["netstat", "-ano"], capture_output=True, text=True, timeout=5)
            for line in r.stdout.splitlines():
                parts = line.split()
                # netstat -ano: "  TCP  0.0.0.0:8000  0.0.0.0:0  LISTENING  1234"
                if len(parts) >= 5 and f":{port}" in parts[1] and "LISTEN" in parts[3]:
                    try:
                        return int(parts[4])
                    except ValueError:
                        pass
        else:
            r = subprocess.run(["lsof", "-ti", f":{port}"], capture_output=True, text=True, timeout=5)
            if r.returncode == 0 and r.stdout.strip():
                return int(r.stdout.strip().splitlines()[0])
    except Exception:
        pass
    return None


def _proc_info_windows(pid: int) -> tuple[str, int | None]:
    """Devuelve (nombre_proceso_lower, parent_pid) en Windows vía PowerShell CIM.

    `wmic` está deprecado/eliminado en Windows 11 reciente, por eso se usa CIM.
    """
    try:
        r = subprocess.run(
            [
                "powershell", "-NoProfile", "-Command",
                f"$p=Get-CimInstance Win32_Process -Filter 'ProcessId={pid}';"
                "if($p){$p.Name; $p.ParentProcessId}",
            ],
            capture_output=True, text=True, timeout=8,
        )
        lines = [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]
        if len(lines) >= 2:
            ppid = int(lines[1]) if lines[1].isdigit() else None
            return lines[0].lower(), ppid
    except Exception:
        pass
    return "", None


# Procesos que forman parte del árbol de un servicio lanzado con `uv run` y que
# es seguro escalar/matar (nunca el shell o la terminal padre).
_KILLABLE_PROC_NAMES = {
    "uv.exe", "uvicorn.exe", "python.exe", "pythonw.exe", "py.exe", "streamlit.exe",
}


def _kill_pid(pid: int) -> bool:
    """Mata el árbol completo del proceso. Devuelve True si tuvo éxito.

    En Windows sube por la cadena de padres mientras sean procesos uv/python
    (el reloader de `uvicorn --reload` es el PADRE del worker que escucha en el
    puerto; matar solo al worker no basta porque el reloader lo respawnea).
    """
    try:
        if IS_WINDOWS:
            roots = [pid]
            cur = pid
            for _ in range(6):
                _name, ppid = _proc_info_windows(cur)
                if not ppid or ppid <= 4:
                    break
                pname, _ = _proc_info_windows(ppid)
                if pname in _KILLABLE_PROC_NAMES:
                    roots.append(ppid)
                    cur = ppid
                else:
                    break
            # Matar desde la raíz hacia abajo, árbol completo (/T).
            for target in reversed(roots):
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(target)],
                    capture_output=True, timeout=8,
                )
        else:
            try:
                os.killpg(os.getpgid(pid), signal.SIGTERM)
                time.sleep(1.5)
                os.killpg(os.getpgid(pid), signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        return True
    except Exception:
        return False


def _pids_by_cmdline(marker: str) -> list[int]:
    """PIDs (Windows) de procesos python/uv cuyo CommandLine contiene `marker`.

    Robusto frente a PIDs «fantasma» de netstat: cuando un proceso que poseía el
    socket (p. ej. el reloader de uvicorn) muere y un hijo hereda el descriptor,
    netstat sigue mostrando el PID muerto. Buscar por línea de comando localiza
    el proceso real que hay que matar.
    """
    if not IS_WINDOWS or not marker:
        return []
    try:
        r = subprocess.run(
            [
                "powershell", "-NoProfile", "-Command",
                "Get-CimInstance Win32_Process | Where-Object { "
                f"$_.CommandLine -like '*{marker}*' -and "
                "$_.Name -in @('python.exe','uv.exe','pythonw.exe','py.exe') } | "
                "Select-Object -ExpandProperty ProcessId",
            ],
            capture_output=True, text=True, timeout=10,
        )
        _self = os.getpid()
        return [
            int(x) for x in r.stdout.split()
            if x.strip().isdigit() and int(x) != _self
        ]
    except Exception:
        return []


def _check_port(port: int) -> bool:
    """True si algo escucha en el puerto."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def _check_health(svc: dict) -> bool:
    """True si el endpoint de salud responde con el texto esperado."""
    try:
        import urllib.request
        url = svc["url"] + svc["health_path"]
        with urllib.request.urlopen(url, timeout=2) as r:
            body = r.read().decode(errors="replace").lower()
            expected = svc.get("health_text", "").lower()
            return expected in body if expected else r.status == 200
    except Exception:
        return False


def _get_state(key: str) -> tuple[str, int | None]:
    """Devuelve (estado, pid).
    estado: 'session' (este script lo arrancó) | 'external' | 'stopped'
    """
    svc = SERVICES[key]
    proc = _session_procs.get(key)
    if proc is not None and proc.poll() is None:
        return "session", proc.pid
    pid = _get_pid_by_port(svc["port"])
    if pid is not None:
        return "external", pid
    return "stopped", None


def _status(key: str) -> str:
    state, pid = _get_state(key)
    svc = SERVICES[key]
    if state == "session":
        live = _check_health(svc)
        badge = c("● CORRIENDO", GREEN) if live else c("● INICIANDO", YELLOW)
        return f"{badge} (:{svc['port']} · pid {pid})"
    if state == "external":
        live = _check_health(svc)
        badge = c("● ACTIVO", CYAN) if live else c("● EN PUERTO", YELLOW)
        return f"{badge} (:{svc['port']} · pid {pid} — externo, detenible)"
    return c("○ DETENIDO", RED)


def _start(key: str) -> None:
    svc = SERVICES[key]
    state, pid = _get_state(key)
    if state in ("session", "external"):
        print(c(f"  {svc['label']} ya está corriendo (pid {pid}).", YELLOW))
        return

    cmd = svc.get("cmd_windows", svc.get("cmd", [])) if IS_WINDOWS else svc.get("cmd_unix", svc.get("cmd", []))
    if not cmd:
        cmd = svc.get("cmd", [])
    if not shutil.which(cmd[0]):
        print(c(f"  ✗ Comando '{cmd[0]}' no encontrado. ¿Está instalado?", RED))
        return

    log_path: Path = svc["log_file"]
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_fh = open(log_path, "w", encoding="utf-8", errors="replace")

    kwargs: dict = {"cwd": str(REPO_ROOT), "stdout": log_fh, "stderr": log_fh}
    if IS_WINDOWS:
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

    print(f"  Arrancando {c(svc['label'], CYAN)} …", end="", flush=True)
    proc = subprocess.Popen(cmd, **kwargs)
    _session_procs[key] = proc

    for _ in range(30):
        time.sleep(0.5)
        print(".", end="", flush=True)
        if _check_port(svc["port"]):
            print(c(" OK", GREEN))
            print(f"  {c('→', BOLD)} {svc['url']}  {DIM}(log: {log_path.name}){RESET}")
            return
        if proc.poll() is not None:
            print(c(" FALLÓ", RED))
            print(f"  Revisa: {log_path}")
            _session_procs.pop(key, None)
            return
    print(c(" timeout (puede seguir iniciándose)", YELLOW))
    print(f"  Log: {log_path}")


def _stop(key: str) -> None:
    """Detiene el servicio ya sea de esta sesión o externo (por PID)."""
    svc = SERVICES[key]
    state, pid = _get_state(key)

    if state == "stopped":
        print(c(f"  {svc['label']} ya está detenido.", YELLOW))
        return

    print(f"  Deteniendo {c(svc['label'], CYAN)} (pid {pid}) …", end="", flush=True)
    killed = False

    # Intentar con Popen si es de esta sesión
    proc = _session_procs.get(key)
    if proc is not None and proc.poll() is None:
        try:
            if IS_WINDOWS:
                proc.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                proc.terminate()
            proc.wait(timeout=6)
            killed = True
        except Exception:
            try:
                proc.kill()
                killed = True
            except Exception:
                pass
        _session_procs.pop(key, None)

    # Si no fue de sesión o Popen falló, matar por PID del OS
    if not killed and pid:
        killed = _kill_pid(pid)

    # Respaldo robusto: si el puerto sigue ocupado (p. ej. PID fantasma de
    # netstat tras morir el reloader de uvicorn), matar por línea de comando.
    if _check_port(svc["port"]):
        marker = svc.get("kill_marker")
        for real_pid in _pids_by_cmdline(marker):
            _kill_pid(real_pid)
            killed = True

    if killed:
        for _ in range(10):
            time.sleep(0.4)
            if not _check_port(svc["port"]):
                break
        print(c(" OK", GREEN))
    else:
        print(c(" no se pudo terminar (prueba como administrador)", RED))


def _tail_log(key: str, lines: int = 35) -> None:
    log_path: Path = SERVICES[key]["log_file"]
    if not log_path.exists():
        print(c(f"  No hay log para {SERVICES[key]['label']}.", YELLOW))
        return
    print(c(f"\n  Últimas {lines} líneas — {log_path.name}:", CYAN))
    print(SEP)
    try:
        text = log_path.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines()[-lines:]:
            print(f"  {line}")
    except Exception as exc:
        print(c(f"  Error: {exc}", RED))
    print(SEP)


# ── Menú ──────────────────────────────────────────────────────────────────────

def _print_header() -> None:
    os.system("cls" if IS_WINDOWS else "clear")
    print(f"\n{BOLD}{CYAN}  🚨  DSS 112 CyL — Gestor de Servicios{RESET}")
    print(f"  {DIM}Repositorio: {REPO_ROOT}{RESET}")
    print(f"  {SEP}")


def _print_status() -> None:
    print(f"\n  {BOLD}Estado de servicios:{RESET}")
    for key, svc in SERVICES.items():
        print(f"    [{c(key, BOLD)}]  {svc['label']:20s}  {_status(key)}")
    print()


def _print_menu() -> None:
    print(f"  {BOLD}Acciones:{RESET}")
    print(f"    {c('1', BOLD)}  Arrancar  Ollama")
    print(f"    {c('2', BOLD)}  Arrancar  Backend FastAPI")
    print(f"    {c('3', BOLD)}  Arrancar  Streamlit UI")
    print(f"    {c('4', BOLD)}  Arrancar  TODOS")
    print()
    print(f"    {c('5', BOLD)}  Detener   Ollama          {DIM}(funciona aunque sea externo){RESET}")
    print(f"    {c('6', BOLD)}  Detener   Backend FastAPI {DIM}(funciona aunque sea externo){RESET}")
    print(f"    {c('7', BOLD)}  Detener   Streamlit UI    {DIM}(funciona aunque sea externo){RESET}")
    print(f"    {c('8', BOLD)}  Detener   TODOS")
    print()
    print(f"    {c('l', BOLD)}  Ver logs   (elige servicio)")
    print(f"    {c('r', BOLD)}  Refrescar  estado")
    print(f"    {c('q', BOLD)}  Salir      (servicios siguen corriendo)")
    print()
    print(f"  {SEP}")


def _ask_service(prompt: str = "Servicio") -> str | None:
    keys = list(SERVICES.keys())
    print(f"\n  {prompt}:")
    for i, k in enumerate(keys, 1):
        print(f"    {i}. {SERVICES[k]['label']}")
    choice = input(f"  [1-{len(keys)}] → ").strip()
    try:
        return keys[int(choice) - 1]
    except (ValueError, IndexError):
        return None


def main() -> None:
    print(c("\n  Iniciando gestor de servicios DSS 112 CyL…\n", CYAN))

    while True:
        _print_header()
        _print_status()
        _print_menu()

        try:
            choice = input(f"  {BOLD}Opción:{RESET} ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print(c("\n\n  Saliendo. Los servicios activos siguen corriendo.\n", YELLOW))
            break

        if choice == "1":
            _start("ollama")
        elif choice == "2":
            _start("backend")
        elif choice == "3":
            _start("ui")
        elif choice == "4":
            print(f"\n  {c('Arrancando todos…', CYAN)}")
            for k in ["ollama", "backend", "ui"]:
                _start(k)
        elif choice == "5":
            _stop("ollama")
        elif choice == "6":
            _stop("backend")
        elif choice == "7":
            _stop("ui")
        elif choice == "8":
            print(f"\n  {c('Deteniendo todos…', CYAN)}")
            for k in ["ui", "backend", "ollama"]:  # inverso para evitar dependencias
                _stop(k)
        elif choice == "l":
            svc_key = _ask_service("¿De qué servicio ver el log?")
            if svc_key:
                _tail_log(svc_key)
            else:
                print(c("  Opción no válida.", RED))
        elif choice in ("r", ""):
            continue
        elif choice == "q":
            print(c("\n  Saliendo. Los servicios activos siguen corriendo.\n", YELLOW))
            break
        else:
            print(c(f"\n  '{choice}' no reconocido.", RED))

        try:
            input(f"\n  {DIM}[Enter para continuar]{RESET}")
        except (KeyboardInterrupt, EOFError):
            break

    sys.exit(0)


    """True si algo escucha en el puerto."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def _check_health(svc: dict) -> bool:
    """True si el endpoint de salud responde correctamente."""
    try:
        import urllib.request
        url = svc["url"] + svc["health_path"]
        with urllib.request.urlopen(url, timeout=2) as r:
            body = r.read().decode(errors="replace").lower()
            expected = svc.get("health_text", "").lower()
            return expected in body if expected else r.status == 200
    except Exception:
        return False

    sys.exit(0)


if __name__ == "__main__":
    main()
