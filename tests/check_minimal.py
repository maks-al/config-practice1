"""Проверка минимальной VFS и параметров запуска."""
from runner import run

run("minimal", ["minimal:/$ ls", "ls (заглушка): []",
                "cd (заглушка): ['/']"])
