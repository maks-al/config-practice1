"""Проверка VFS с несколькими файлами и кавычками."""
from runner import run

run("files", ["ls (заглушка): ['hello world.txt']",
              "cd (заглушка): ['folder with spaces']"])
