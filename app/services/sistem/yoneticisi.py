# -*- coding: utf-8 -*-
"""
DOSYA: app/services/sistem/yoneticisi.py

ROL:
- Sistem katmanına tek giriş noktası sağlamak
- UI ve diğer katmanların alt sistem servis detaylarını bilmesini engellemek
- Ayar, uygulama durumu, dil, geçici bildirim ve premium akışlarını merkezileştirmek
- İleride sistem servisleri büyüdüğünde tek noktadan yönetim sağlamak
- diller/ klasöründeki json dosyalarını otomatik algılayan dil servisini dış katmanlara sunmak

MİMARİ:
- Alt sistem servislerine lazy import ile erişir
- UI katmanı sadece bu yöneticiyi bilir
- Sistem katmanının iç yapısını dış dünyadan saklar
- Ayar, uygulama durumu, dil, bildirim ve premium davranışını tek yerden toplar
- Dil listesi sabit değil, dil servisi ve ayar servisi üzerinden dinamik yürür
- Geçici bildirim servisinin gelişmiş show parametrelerini güvenli biçimde aşağı iletir
- Dil servisi tek instance olarak tutulur; her çağrıda yeniden üretilmez

API UYUMLULUK:
- API 35 uyumlu
- AndroidX ile çakışmaz
- Platform bağımsız yardımcı servislerle güvenli çalışır
- Android bridge kullanan premium servisini güvenli fallback ile çağırır

SURUM: 6
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations


class SistemYoneticisi:
    _dil_servisi_instance = None

    # =========================================================
    # INTERNAL
    # =========================================================
    def _dil_servisi(self):
        if SistemYoneticisi._dil_servisi_instance is None:
            from app.services.sistem.dil_servisi import DilServisi
            SistemYoneticisi._dil_servisi_instance = DilServisi()
        return SistemYoneticisi._dil_servisi_instance

    # =========================================================
    # AYAR
    # =========================================================
    def ayarlari_yukle(self) -> dict:
        from app.services.sistem.ayar_servisi import ayarlari_yukle
        return ayarlari_yukle()

    def ayarlari_kaydet(self, data: dict) -> None:
        from app.services.sistem.ayar_servisi import ayarlari_kaydet
        ayarlari_kaydet(data)

    def get_language(self, default: str = "tr") -> str:
        from app.services.sistem.ayar_servisi import get_language
        return get_language(default=default)

    def set_language(self, code: str) -> None:
        from app.services.sistem.ayar_servisi import set_language
        set_language(code)

    def supported_languages(self) -> list[str]:
        try:
            return self.mevcut_dil_kodlari()
        except Exception:
            from app.services.sistem.ayar_servisi import supported_languages
            return supported_languages()

    def language_supported(self, code: str) -> bool:
        try:
            return self.dil_destekleniyor_mu(code)
        except Exception:
            from app.services.sistem.ayar_servisi import language_supported
            return language_supported(code)

    # =========================================================
    # DIL
    # =========================================================
    def aktif_dil(self) -> str:
        return self._dil_servisi().aktif_dil()

    def dil_degistir(self, code: str) -> bool:
        return self._dil_servisi().dil_degistir(code)

    def set_active_language(self, code: str) -> bool:
        return self._dil_servisi().set_active_language(code)

    def aktif_dili_ayardan_yukle(self, default: str = "tr") -> str:
        return self._dil_servisi().aktif_dili_ayardan_yukle(default=default)

    def dil_destekleniyor_mu(self, code: str) -> bool:
        return self._dil_servisi().dil_destekleniyor_mu(code)

    def dil_var_mi(self, code: str) -> bool:
        return self._dil_servisi().dil_var_mi(code)

    def mevcut_dilleri_listele(self) -> list[dict[str, str]]:
        return self._dil_servisi().mevcut_dilleri_listele()

    def mevcut_dil_kodlari(self) -> list[str]:
        return self._dil_servisi().mevcut_dil_kodlari()

    def dilleri_yeniden_tara(self) -> list[dict[str, str]]:
        return self._dil_servisi().dilleri_yeniden_tara()

    def desteklenen_diller(
        self,
        sadece_aktifler: bool = False,
    ) -> dict[str, dict[str, object]]:
        return self._dil_servisi().desteklenen_diller(
            sadece_aktifler=sadece_aktifler
        )

    def dil_adi(self, code: str, default: str = "") -> str:
        return self._dil_servisi().dil_adi(code=code, default=default)

    def metin(self, anahtar: str, default: str = "") -> str:
        return self._dil_servisi().metin(anahtar=anahtar, varsayilan=default)

    # =========================================================
    # APP STATE
    # =========================================================
    def get_app_state(self, default: dict | None = None) -> dict:
        from app.services.sistem.ayar_servisi import get_app_state
        return get_app_state(default=default)

    def set_app_state(self, state: dict) -> None:
        from app.services.sistem.ayar_servisi import set_app_state
        set_app_state(state)

    def clear_app_state(self) -> None:
        from app.services.sistem.ayar_servisi import clear_app_state
        clear_app_state()

    # =========================================================
    # GECICI BILDIRIM
    # =========================================================
    def register_bildirim_layer(self, layer) -> bool:
        from app.services.sistem.gecici_bildirim_servisi import (
            gecici_bildirim_servisi,
        )
        return gecici_bildirim_servisi.register_layer(layer)

    def unregister_bildirim_layer(self) -> None:
        from app.services.sistem.gecici_bildirim_servisi import (
            gecici_bildirim_servisi,
        )
        gecici_bildirim_servisi.unregister_layer()

    def bildirim_layer_var_mi(self) -> bool:
        from app.services.sistem.gecici_bildirim_servisi import (
            gecici_bildirim_servisi,
        )
        return gecici_bildirim_servisi.has_layer()

    def bildirim_goster(
        self,
        text: str,
        icon_name: str = "",
        duration: float = 2.4,
        title: str = "",
        tone: str = "info",
        on_tap=None,
    ) -> bool:
        from app.services.sistem.gecici_bildirim_servisi import (
            gecici_bildirim_servisi,
        )
        return gecici_bildirim_servisi.show(
            text=text,
            icon_name=icon_name,
            duration=duration,
            title=title,
            tone=tone,
            on_tap=on_tap,
        )

    def bildirim_gizle(self) -> bool:
        from app.services.sistem.gecici_bildirim_servisi import (
            gecici_bildirim_servisi,
        )
        return gecici_bildirim_servisi.hide()

    def bildirimi_aninda_gizle(self) -> bool:
        from app.services.sistem.gecici_bildirim_servisi import (
            gecici_bildirim_servisi,
        )
        return gecici_bildirim_servisi.hide_immediately()

    # =========================================================
    # PREMIUM
    # =========================================================
    def premium_aktif_mi(self) -> bool:
        from app.services.sistem.premium_servisi import premium_servisi
        return premium_servisi.premium_aktif_mi()
