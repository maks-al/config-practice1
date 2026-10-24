"""Графический эмулятор UNIX-оболочки, вариант 1, этапы 1–3."""
import argparse
from pathlib import Path
import sys
import tkinter as tk

from src.shell import Shell
from src.vfs import VFS

ROOT = Path(__file__).resolve().parent


class App:
    """Один терминал: журнал и ввод команд в одном окне."""

    def __init__(self, window, vfs, vfs_path="", script_path=""):
        self.window = window
        self.prompt = f"{vfs.name}:/$ "
        self.command = ""
        self.cursor = 0
        self.ready = False
        self.shell = Shell(vfs, self.write)

        window.title(f"{vfs.name}")
        window.geometry("900x550")
        window.minsize(540, 300)

        # Один виджет для вывода и ввода, как в обычном терминале.
        self.log = tk.Text(window, font=("Consolas", 12), wrap="word",
                           state="disabled", undo=False)
        self.log.pack(fill="both", expand=True, padx=8, pady=8)
        self.log.bind("<KeyPress>", self.on_key)
        self.log.bind("<<Paste>>", self.on_paste)
        self.log.focus_set()

        self.write(f"Параметры: VFS={vfs_path or vfs.source}; "
                   f"script={script_path or 'нет'}")
        self.write(f"VFS: {vfs.name}; папок: {len(vfs.dirs)}; "
                   f"файлов: {len(vfs.files)}")
        for path in sorted(vfs.dirs | vfs.files.keys()):
            self.write("  " + path)
        self.write("Команды: ls, cd, exit (ls и cd пока заглушки)")
        if not script_path:
            self.show_prompt()

    def append(self, text):
        """Дописывать текст программно, не разрешая менять журнал."""
        self.log.config(state="normal")
        self.log.insert("end-1c", text)
        self.log.config(state="disabled")
        self.log.see("end")

    def write(self, message):
        """Показать вывод команды в GUI и в обычной консоли."""
        self.append(message + "\n")
        if sys.stdout is not None:
            print(message, flush=True)

    def show_prompt(self):
        """Напечатать приглашение и начать новую строку ввода."""
        self.append(self.prompt)
        self.log.mark_set("input_start", "end-1c")
        self.log.mark_gravity("input_start", "left")
        self.command = ""
        self.cursor = 0
        self.ready = True
        self.log.focus_set()

    def redraw(self):
        """Изменять только текст правее приглашения."""
        self.log.config(state="normal")
        self.log.delete("input_start", "end-1c")
        self.log.insert("end-1c", self.command)
        self.log.mark_set("insert", f"input_start + {self.cursor} chars")
        self.log.config(state="disabled")
        self.log.see("end")

    def type_text(self, text):
        """Вставить символы в текущую команду."""
        if not self.ready:
            return
        text = text.replace("\r", "").replace("\n", " ")
        self.command = (self.command[:self.cursor] + text
                        + self.command[self.cursor:])
        self.cursor += len(text)
        self.redraw()

    def on_paste(self, _event=None):
        """Вставка из буфера обмена не меняет предыдущие строки."""
        try:
            self.type_text(self.window.clipboard_get())
        except tk.TclError:
            pass
        return "break"

    def copy_selection(self):
        """Разрешить Ctrl+C для выделенного текста терминала."""
        try:
            text = self.log.get("sel.first", "sel.last")
            self.window.clipboard_clear()
            self.window.clipboard_append(text)
        except tk.TclError:
            pass

    def on_key(self, event):
        """Направить клавиши ввода в текущую команду."""
        if not self.ready:
            return "break"
        key = event.keysym
        ctrl = bool(event.state & 0x4)
        if ctrl and key.lower() == "v":
            return self.on_paste()
        if ctrl and key.lower() == "c":
            self.copy_selection()
        elif not ctrl and key in ("Return", "KP_Enter"):
            self.submit()
        elif not ctrl:
            self.edit_key(key, event.char)
        return "break"

    def edit_key(self, key, char):
        """Редактировать только текст команды, не историю терминала."""
        if key == "BackSpace" and self.cursor:
            self.command = (self.command[:self.cursor - 1]
                            + self.command[self.cursor:])
            self.cursor -= 1
        elif key == "Delete" and self.cursor < len(self.command):
            self.command = (self.command[:self.cursor]
                            + self.command[self.cursor + 1:])
        elif key == "Left":
            self.cursor = max(0, self.cursor - 1)
        elif key == "Right":
            self.cursor = min(len(self.command), self.cursor + 1)
        elif key == "Home":
            self.cursor = 0
        elif key == "End":
            self.cursor = len(self.command)
        elif char and char.isprintable():
            self.type_text(char)
        if self.ready:
            self.redraw()

    def submit(self):
        """Выполнить введённую команду и показать новый prompt."""
        if not self.ready:
            return
        line = self.command
        self.ready = False
        self.append("\n")
        if sys.stdout is not None:
            print(self.prompt + line, flush=True)
        self.shell.execute(line, echo=False)
        if not self.shell.running:
            self.window.destroy()
        else:
            self.show_prompt()

    def startup(self, filename):
        """Выполнить стартовый скрипт и перейти к ручному вводу."""
        self.shell.run_script(filename)
        if not self.shell.running:
            self.window.destroy()
        else:
            self.show_prompt()


def main():
    """Загрузить VFS и открыть окно терминала."""
    parser = argparse.ArgumentParser(description="Вариант 1, этапы 1–3")
    parser.add_argument("--vfs", default=str(ROOT / "examples/minimal.json"))
    parser.add_argument("--script", help="путь к стартовому скрипту")
    args = parser.parse_args()
    try:
        vfs = VFS(args.vfs)
    except (OSError, ValueError) as exc:
        print(f"Ошибка VFS: {exc}", file=sys.stderr)
        return 1
    try:
        window = tk.Tk()
    except tk.TclError as exc:
        print(f"Не удалось открыть окно: {exc}", file=sys.stderr)
        return 1
    app = App(window, vfs, args.vfs, args.script)
    if args.script:
        window.after(100, lambda: app.startup(args.script))
    window.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
