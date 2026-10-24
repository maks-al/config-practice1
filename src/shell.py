"""Эмулятор команд-заглушек и стартового скрипта."""
import shlex
from pathlib import Path

CD_MAX_ARGS = 1


class Shell:
    """Состояние REPL: VFS, вывод и признак работы."""

    def __init__(self, vfs, write):
        """Получить VFS и функцию вывода строк."""
        self.vfs = vfs
        self.write = write
        self.running = True

    def execute(self, line, echo=True):
        """Разобрать и выполнить одну строку, вернуть успех/ошибку."""
        if echo:
            self.write(f"{self.vfs.name}:/$ {line}")
        try:
            words = shlex.split(line)  # Корректно обрабатывает кавычки.
        except ValueError as exc:
            self.write(f"Ошибка кавычек: {exc}")
            return False
        if not words:
            return True
        command, *args = words
        if command in ("ls", "cd"):
            if command == "cd" and len(args) > CD_MAX_ARGS:
                self.write("Ошибка: cd принимает максимум один аргумент")
                return False
            self.write(f"{command}: {args}")
        elif command == "exit":
            if args:
                self.write("Ошибка: exit не принимает аргументы")
                return False
            self.write("Выход из эмулятора")
            self.running = False
        else:
            self.write(f"Ошибка: неизвестная команда: {command}")
            return False
        return True

    def run_script(self, filename):
        """Выполнить файл команд, остановиться при первой ошибке."""
        try:
            lines = Path(filename).read_text(encoding="utf-8-sig").splitlines()
        except OSError as exc:
            self.write(f"Ошибка чтения скрипта: {exc}")
            return False
        for number, line in enumerate(lines, 1):
            if not line.strip() or line.lstrip().startswith("#"):
                continue  # Пропускаем комментарии и пустые строки.
            if not self.execute(line):
                self.write(f"Скрипт остановлен из-за ошибки в строке {number}")
                return False
            if not self.running:
                break
        return True
