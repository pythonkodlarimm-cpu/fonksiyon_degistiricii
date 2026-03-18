# -*- coding: utf-8 -*-
"""
DOSYA: app/config.py

BURADAN AÇ / KAPAT:
- True  -> test modu açık
- False -> test modu kapalı
"""

from __future__ import annotations


# =========================================================
# SADE AYARLAR
# =========================================================

DEV_MODE = False
DEBUG_LOG = DEV_MODE

AUTO_BACKUP_ON_UPDATE = True
AUTO_VALIDATE_AFTER_UPDATE = True
TEST_MODE_VERBOSE = DEV_MODE


# =========================================================
# YARDIMCI
# =========================================================
def debug_print(msg: str) -> None:
    if DEBUG_LOG:
        try:
            print("[CONFIG]", str(msg))
        except Exception:
            pass