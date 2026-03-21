# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dosya_secici_paketi/yoneticisi.py

ROL:
- Dosya seçici paketine tek giriş noktası sağlamak
- Picker, popup ve geliştirici mod alt paketlerini merkezileştirmek
- Dosya seçici widget'ının alt modülleri doğrudan bilmesini engellemek
- Başlangıç klasörü, seçim modelleri ve popup akışını tek yerden sunmak

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Picker, popup ve geliştirici mod alt paketleri yöneticileri üzerinden çağrılır
- Helper ve model erişimi burada toplanır
- Paket dışına alt modül detayları sızdırılmaz

API UYUMLULUK:
- Android SAF akışıyla uyumludur
- Masaüstü path tabanlı akışla uyumludur
- API 35 uyumludur

SURUM: 2
TARIH: 2026-03-20
IMZA: FY.
"""

from __future__ import annotations


class DosyaSeciciYoneticisi:
    # =========================================================
    # PICKER
    # =========================================================
    def _picker_yoneticisi(self):
        from app.ui.dosya_secici_paketi.pickers import PickerYoneticisi
        return PickerYoneticisi()

    def picker_olustur(self, owner, on_selected):
        return self._picker_yoneticisi().picker_olustur(
            owner=owner,
            on_selected=on_selected,
        )

    def picker_ac(self, owner, on_selected):
        return self._picker_yoneticisi().picker_ac(
            owner=owner,
            on_selected=on_selected,
        )

    # =========================================================
    # POPUP
    # =========================================================
    def _popup_yoneticisi(self):
        from app.ui.dosya_secici_paketi.popup import PopupYoneticisi
        return PopupYoneticisi()

    def bilgi_goster(self, owner, title: str, message: str):
        return self._popup_yoneticisi().bilgi_goster(
            owner=owner,
            title=title,
            message=message,
        )

    # =========================================================
    # GELISTIRICI MOD
    # =========================================================
    def _gelistirici_mod_yoneticisi(self):
        from app.ui.dosya_secici_paketi.gelistirici_mod import GelistiriciModYoneticisi
        return GelistiriciModYoneticisi()

    def dev_mode_aktif_mi(self) -> bool:
        return self._gelistirici_mod_yoneticisi().dev_mode_aktif_mi()

    def test_popup_ac(self, on_select=None, start_dir: str | None = None):
        return self._gelistirici_mod_yoneticisi().test_popup_ac(
            on_select=on_select,
            start_dir=start_dir,
        )

    def test_selection_olustur(self, path: str):
        return self._gelistirici_mod_yoneticisi().test_selection_olustur(path)

    # =========================================================
    # HELPERS
    # =========================================================
    def varsayilan_baslangic_klasoru(self):
        from app.ui.dosya_secici_paketi.helpers import varsayilan_baslangic_klasoru
        return varsayilan_baslangic_klasoru()

    # =========================================================
    # MODELS
    # =========================================================
    def document_selection_class(self):
        from app.ui.dosya_secici_paketi.models import DocumentSelection
        return DocumentSelection

    def document_session_class(self):
        from app.ui.dosya_secici_paketi.models import DocumentSession
        return DocumentSession