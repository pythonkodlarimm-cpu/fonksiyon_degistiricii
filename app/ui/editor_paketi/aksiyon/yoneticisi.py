# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/aksiyon/yoneticisi.py

ROL:
- Aksiyon alt paketine tek giriş noktası sağlamak
- Editör panelindeki kullanıcı aksiyonlarını merkezileştirmek
- Üst katmanın aksiyon modülü detaylarını bilmesini engellemek
- Aksiyon çağrılarını güvenli ve kontrollü biçimde alt modüle yönlendirmek

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt aksiyon modülü doğrudan dışarı açılmaz
- Kopyalama, temizleme, doğrulama, güncelleme ve geri yükleme akışlarını toplar
- Lazy import kullanır
- Fail-soft yaklaşım için tanılama logu bırakır

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 2
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

import traceback


class AksiyonYoneticisi:
    def _modul(self):
        try:
            from app.ui.editor_paketi.aksiyon.editor_aksiyonlari import (
                check_new_code,
                clear_new_code,
                copy_current_to_new,
                handle_restore,
                handle_update,
            )

            return {
                "copy_current_to_new": copy_current_to_new,
                "clear_new_code": clear_new_code,
                "check_new_code": check_new_code,
                "handle_update": handle_update,
                "handle_restore": handle_restore,
            }
        except Exception:
            print("[EDITOR_AKSIYON_YONETICI] Aksiyon modülü yüklenemedi.")
            print(traceback.format_exc())
            raise

    def copy_current_to_new(self, panel, *_args):
        try:
            return self._modul()["copy_current_to_new"](panel, *_args)
        except Exception:
            print("[EDITOR_AKSIYON_YONETICI] copy_current_to_new çağrısı başarısız.")
            print(traceback.format_exc())
            raise

    def clear_new_code(self, panel, *_args):
        try:
            return self._modul()["clear_new_code"](panel, *_args)
        except Exception:
            print("[EDITOR_AKSIYON_YONETICI] clear_new_code çağrısı başarısız.")
            print(traceback.format_exc())
            raise

    def check_new_code(self, panel, *_args):
        try:
            return self._modul()["check_new_code"](panel, *_args)
        except Exception:
            print("[EDITOR_AKSIYON_YONETICI] check_new_code çağrısı başarısız.")
            print(traceback.format_exc())
            raise

    def handle_update(self, panel, *_args):
        try:
            return self._modul()["handle_update"](panel, *_args)
        except Exception:
            print("[EDITOR_AKSIYON_YONETICI] handle_update çağrısı başarısız.")
            print(traceback.format_exc())
            raise

    def handle_restore(self, panel, *_args):
        try:
            return self._modul()["handle_restore"](panel, *_args)
        except Exception:
            print("[EDITOR_AKSIYON_YONETICI] handle_restore çağrısı başarısız.")
            print(traceback.format_exc())
            raise
