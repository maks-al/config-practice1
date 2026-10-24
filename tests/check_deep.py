"""Проверка VFS с тремя уровнями вложенности."""
from runner import run

run("deep", ["/one/two/three/task.txt",
             "ls (заглушка): ['/one/two/three']",
             "cd (заглушка): ['/one']"])
