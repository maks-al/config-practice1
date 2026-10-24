"""Запуск эмулятора как отдельной программы (виден ввод и вывод)."""
import subprocess
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(name, expected):
    """Проверить параметры, скрипт, команды и завершение окна."""
    command = [sys.executable, str(ROOT / "run.py"),
               "--vfs", str(ROOT / "examples" / f"{name}.json"),
               "--script", str(ROOT / "examples" / f"check_{name}.txt")]
    print("\nЗАПУСК:", " ".join(command), flush=True)
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    result = subprocess.run(command, text=True, capture_output=True,
                            encoding="utf-8", errors="replace",
                            timeout=15, env=env)
    print(result.stdout, end="", flush=True)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    assert result.returncode == 0, "ошибка запуска GUI"
    for phrase in [f"VFS: {name}", *expected, "Выход из эмулятора"]:
        assert phrase in result.stdout, f"не найдено: {phrase}"
    print(f"PASS: {name} — запуск, команды и exit", flush=True)
