"""Простая виртуальная файловая система из JSON (только в памяти)."""
import base64
import binascii
import json
from pathlib import Path


def normalize_path(raw):
    """Проверить и привести путь к единому виду '/папка/файл'."""
    if not isinstance(raw, str) or not raw.startswith("/"):
        raise ValueError("VFS: путь должен начинаться с /")
    if "\\" in raw or "\x00" in raw:
        raise ValueError("VFS: недопустимые символы в пути")
    parts = raw.split("/")
    if any(part in (".", "..") for part in parts):
        raise ValueError("VFS: запрещены . и .. в пути")
    return "/" + "/".join(part for part in parts if part)


def file_content(item):
    """Получить байты файла из обычного текста или Base64."""
    if "base64" in item:
        if "content" in item or not isinstance(item["base64"], str):
            raise ValueError("VFS: неверное поле base64")
        try:
            return base64.b64decode(item["base64"], validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError("VFS: неверный base64") from exc
    text = item.get("content", "")
    if not isinstance(text, str):
        raise ValueError("VFS: content должен быть строкой")
    return text.encode("utf-8")


class VFS:
    """Каталоги хранятся во множестве, файлы — в словаре с байтами."""

    def __init__(self, filename):
        """Считать JSON один раз; оригинальный файл не изменять."""
        self.source = Path(filename)
        data = json.loads(self.source.read_text(encoding="utf-8-sig"))
        if not isinstance(data, dict):
            raise ValueError("VFS: JSON должен быть объектом")
        if not isinstance(data.get("entries"), list):
            raise ValueError("VFS: ожидается список entries")
        self.name = data.get("name", self.source.stem)
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("VFS: неверное имя")
        self.dirs = {"/"}
        self.files = {}
        self.used = set()
        for item in data["entries"]:
            self.add_entry(item)

    def add_entry(self, item):
        """Добавить запись и недостающие родительские папки."""
        if not isinstance(item, dict):
            raise ValueError("VFS: запись должна быть объектом")
        path = normalize_path(item.get("path"))
        kind = item.get("type")
        if kind not in ("dir", "file") or path in self.used:
            raise ValueError(f"VFS: неверный тип или повтор пути: {path}")
        self.used.add(path)
        parts = path.strip("/").split("/") if path != "/" else []
        for index in range(1, len(parts)):
            parent = "/" + "/".join(parts[:index])
            if parent in self.files:
                raise ValueError(f"VFS: файл вместо папки: {parent}")
            self.dirs.add(parent)
        if kind == "dir":
            if path in self.files:
                raise ValueError(f"VFS: файл вместо папки: {path}")
            self.dirs.add(path)
        else:
            if path in self.dirs:
                raise ValueError(f"VFS: папка вместо файла: {path}")
            self.files[path] = file_content(item)
