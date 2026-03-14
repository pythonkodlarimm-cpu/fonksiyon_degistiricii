# -*- coding: utf-8 -*-

from __future__ import annotations

import os
import shutil


def read_text(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def write_text(file_path: str, content: str) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def backup_file(file_path: str) -> str:
    backup_path = file_path + ".bak"
    shutil.copyfile(file_path, backup_path)
    return backup_path


def exists(file_path: str) -> bool:
    return os.path.isfile(file_path)