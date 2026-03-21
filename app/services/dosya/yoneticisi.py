# -*- coding: utf-8 -*-
"""
DOSYA: app/services/dosya/yoneticisi.py

ROL:
- Dosya servislerine tek giriş noktası sağlamak
- UI ve diğer katmanların alt servis detaylarını bilmesini engellemek
- Path tabanlı dosya işlemlerini merkezileştirmek
- Güvenli, doğrulanabilir ve izole dosya erişimi sağlamak

MİMARİ:
- Tüm çağrılar lazy import ile yapılır
- Alt servis (servisi.py) doğrudan dışarı açılmaz
- Manager üzerinden erişim zorunlu hale getirilir
- Android URI işlemleri burada yapılmaz (android katmanında kalır)

API UYUMLULUK:
- API 35 uyumlu
- Scoped storage ile çakışmaz
- Local file system güvenli erişim sağlar

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from pathlib import Path


class DosyaYoneticisi:
    # =========================================================
    # READ / WRITE
    # =========================================================
    def read_text(self, file_path: str | Path, encoding: str = "utf-8") -> str:
        from app.services.dosya.servisi import read_text
        return read_text(file_path, encoding=encoding)

    def write_text(self, file_path: str | Path, content: str, encoding: str = "utf-8") -> None:
        from app.services.dosya.servisi import write_text
        write_text(file_path, content, encoding=encoding)

    # =========================================================
    # FILE STATE
    # =========================================================
    def exists(self, file_path: str | Path) -> bool:
        from app.services.dosya.servisi import exists
        return exists(file_path)

    def get_display_name(self, file_path: str | Path) -> str:
        from app.services.dosya.servisi import get_display_name
        return get_display_name(file_path)

    # =========================================================
    # BACKUP
    # =========================================================
    def backup_file(self, file_path: str | Path) -> str:
        from app.services.dosya.servisi import backup_file
        return backup_file(file_path)

    # =========================================================
    # ROOT
    # =========================================================
    def get_app_working_root(self) -> Path:
        from app.services.dosya.servisi import get_app_working_root
        return get_app_working_root()

    def get_app_backups_root(self) -> Path:
        from app.services.dosya.servisi import get_app_backups_root
        return get_app_backups_root()