"""Проверка команд, скриптов и трёх VFS: python tests.py."""
import subprocess
import os
import sys
import tkinter as tk
from pathlib import Path
from types import SimpleNamespace

from run import App

from src.shell import Shell
from src.vfs import VFS

ROOT = Path(__file__).resolve().parent
EXAMPLES = ROOT / "examples"
count = 0


def passed(name):
    """Напечатать итог проверки."""
    global count
    count += 1
    print("PASS:", name, flush=True)


def test_commands():
    """Проверить команды-заглушки, ошибки, кавычки и выход."""
    output = []

    def show(text):
        print(text, flush=True)
        output.append(text)

    shell = Shell(VFS(EXAMPLES / "minimal.json"), show)
    cases = [
        ("ls", "ls (заглушка): []", True),
        ("cd /one", "cd (заглушка): ['/one']", True),
        ('ls "two words.txt"', "['two words.txt']", True),
        ('cd "my folder"', "['my folder']", True),
        ("wrong-command", "неизвестная команда", False),
        ('ls "unfinished', "Ошибка кавычек", False),
        ("cd one two", "максимум один аргумент", False),
        ("exit extra", "exit не принимает аргументы", False),
        ("exit", "Выход из эмулятора", True),
    ]
    for command, expected, correct in cases:
        output.clear()
        print("\n>>> ", command, sep="", flush=True)
        result = shell.execute(command)
        assert result is correct, f"Неверный статус: {command}"
        assert any(expected in line for line in output), command
        passed(command)
    assert not shell.running, "exit не завершил оболочку"


def test_scripts():
    """Проверить успешный скрипт и остановку на первой ошибке."""
    for filename, success in [
        ("startup_ok.txt", True),
        ("startup_error.txt", False),
    ]:
        output = []
        print("\n=== Стартовый скрипт:", filename, "===", flush=True)

        def show(text):
            print(text, flush=True)
            output.append(text)

        shell = Shell(VFS(EXAMPLES / "deep.json"), show)
        assert shell.run_script(EXAMPLES / filename) is success
        if success:
            assert not shell.running, "exit из скрипта не выполнился"
        else:
            assert shell.running, "ошибка закрыла оболочку"
            assert any("Скрипт остановлен" in x for x in output)
            assert not any("cd (заглушка): ['THIS_MUST_NOT_RUN']" in x
                           for x in output)
        passed(filename)


def test_vfs():
    """Проверить три варианта VFS, Base64 и чтение без записи."""
    for name in ("minimal", "files", "deep"):
        path = EXAMPLES / f"{name}.json"
        before = path.read_bytes()
        vfs = VFS(path)
        print(f"\nVFS {name}: {len(vfs.dirs)} папок, "
              f"{len(vfs.files)} файлов", flush=True)
        assert vfs.name == name
        if name == "minimal":
            assert vfs.dirs == {"/"} and not vfs.files
        elif name == "files":
            assert vfs.files["/picture.bin"] == bytes([0, 1, 2, 3, 255, 254])
        else:
            assert "/one/two/three" in vfs.dirs
            assert "/one/two/three/task.txt" in vfs.files
        assert path.read_bytes() == before, "файл VFS изменён"
        passed("JSON-VFS " + name)


def test_gui_scripts():
    """Проверить запуск настоящего GUI с параметрами и auto-exit."""
    try:
        window = tk.Tk()
        window.withdraw()
        window.destroy()
    except tk.TclError:
        print("\nSKIP: GUI-тесты (нет графического дисплея)")
        return
    # Ввод exit непосредственно в окно, а не только из файла.
    window = tk.Tk()
    window.withdraw()
    app = App(window, VFS(EXAMPLES / "minimal.json"))
    for char in "exit":
        app.on_key(SimpleNamespace(keysym=char, char=char, state=0))
    app.on_key(SimpleNamespace(keysym="Return", char="\r", state=0))
    assert not app.shell.running, "Enter не выполнил exit"
    passed("GUI — ввод exit через Enter")

    for name in ("minimal", "files", "deep"):
        command = [sys.executable, str(ROOT / "tests" / f"check_{name}.py")]
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        result = subprocess.run(command, text=True, capture_output=True,
                                encoding="utf-8", errors="replace",
                                timeout=20, env=env)
        print("\n" + result.stdout, end="", flush=True)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        assert result.returncode == 0, name
        passed("GUI " + name)


def main():
    """Запустить проверки; при ошибке вернуть ненулевой код."""
    try:
        test_commands()
        test_scripts()
        test_vfs()
        test_gui_scripts()
    except (AssertionError, OSError, subprocess.TimeoutExpired) as error:
        print("FAIL:", error, file=sys.stderr)
        return 1
    print(f"\nГОТОВО: пройдено {count} проверок")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
