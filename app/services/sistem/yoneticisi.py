# -*- coding: utf-8 -*-
"""
DOSYA: app/services/sistem/yoneticisi.py

ROL:
- Sistem katmanına tek giriş noktası sağlamak
- UI ve diğer katmanların alt sistem servis detaylarını bilmesini engellemek
- Ayar, uygulama durumu, dil, geçici bildirim ve premium akışlarını merkezileştirmek
- İleride sistem servisleri büyüdüğünde tek noktadan yönetim sağlamak
- diller/ klasöründeki json dosyalarını otomatik algılayan dil servisini dış katmanlara sunmak
- Android / APK / AAB ortamında dil servisini tek instance ve güvenli cache ile çalıştırmak

MİMARİ:
- Alt sistem servislerine lazy import ile erişir
- UI katmanı sadece bu yöneticiyi bilir
- Sistem katmanının iç yapısını dış dünyadan saklar
- Ayar, uygulama durumu, dil, bildirim ve premium davranışını tek yerden toplar
- Dil listesi sabit değil, dil servisi ve ayar servisi üzerinden dinamik yürür
- Geçici bildirim servisinin gelişmiş show parametrelerini güvenli biçimde aşağı iletir
- Dil servisi tek instance olarak tutulur; her çağrıda yeniden üretilmez
- Modül ve servis erişimleri instance cache ile optimize edilir
- Mevcut davranış korunur; sadece lazy import ve Android uyumluluğu güçlendirilir

API UYUMLULUK:
- API 35 uyumlu
- AndroidX ile çakışmaz
- Platform bağımsız yardımcı servislerle güvenli çalışır
- Android bridge kullanan premium servisini güvenli fallback ile çağırır

SURUM: 7
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

import traceback


class SistemYoneticisi:
    _dil_servisi_instance = None

    def __init__(self) -> None:
        self._modul_cache: dict[str, object] = {}
        self._servis_cache: dict[str, object] = {}

    # =========================================================
    # INTERNAL CACHE
    # =========================================================
    def cache_temizle(self) -> None:
        """
        Yönetici içindeki modül ve servis cache'lerini temizler.
        """
        try:
            self._modul_cache = {}
        except Exception:
            pass

        try:
            self._servis_cache = {}
        except Exception:
            pass

    def _modul_yukle(self, modul_yolu: str):
        """
        Hedef modülü lazy import + cache ile yükler.

        Args:
            modul_yolu: Modül yolu.

        Returns:
            module | None
        """
        try:
            cached = self._modul_cache.get(modul_yolu)
            if cached is not None:
                return cached
        except Exception:
            pass

        try:
            modul = __import__(modul_yolu, fromlist=["*"])
            self._modul_cache[modul_yolu] = modul
            return modul
        except Exception:
            print(f"[SISTEM_YONETICISI] Modül yüklenemedi: {modul_yolu}")
            print(traceback.format_exc())
            return None

    def _modul_fonksiyonu(self, modul_yolu: str, fonksiyon_adi: str):
        """
        Modül içindeki fonksiyonu döndürür.

        Args:
            modul_yolu: Modül yolu.
            fonksiyon_adi: Fonksiyon adı.

        Returns:
            callable | None
        """
        cache_key = f"{modul_yolu}::{fonksiyon_adi}"

        try:
            cached = self._servis_cache.get(cache_key)
            if callable(cached):
                return cached
        except Exception:
            pass

        modul = self._modul_yukle(modul_yolu)
        if modul is None:
            return None

        try:
            fn = getattr(modul, fonksiyon_adi, None)
            if callable(fn):
                self._servis_cache[cache_key] = fn
                return fn
        except Exception:
            print(
                "[SISTEM_YONETICISI] Fonksiyon alınamadı: "
                f"{modul_yolu}.{fonksiyon_adi}"
            )
            print(traceback.format_exc())

        return None

    def _modul_nesnesi(self, modul_yolu: str, nesne_adi: str):
        """
        Modül içindeki nesneyi döndürür.

        Args:
            modul_yolu: Modül yolu.
            nesne_adi: Nesne adı.

        Returns:
            object | None
        """
        cache_key = f"{modul_yolu}::{nesne_adi}"

        try:
            cached = self._servis_cache.get(cache_key)
            if cached is not None:
                return cached
        except Exception:
            pass

        modul = self._modul_yukle(modul_yolu)
        if modul is None:
            return None

        try:
            obj = getattr(modul, nesne_adi, None)
            if obj is not None:
                self._servis_cache[cache_key] = obj
                return obj
        except Exception:
            print(
                "[SISTEM_YONETICISI] Nesne alınamadı: "
                f"{modul_yolu}.{nesne_adi}"
            )
            print(traceback.format_exc())

        return None

    # =========================================================
    # DIL SERVISI
    # =========================================================
    def _dil_servisi(self):
        """
        Tekil DilServisi instance'ını döndürür.
        """
        if SistemYoneticisi._dil_servisi_instance is None:
            modul = self._modul_yukle("app.services.sistem.dil_servisi")
            if modul is None:
                raise RuntimeError("Dil servisi modülü yüklenemedi.")

            cls = getattr(modul, "DilServisi", None)
            if cls is None:
                raise RuntimeError("DilServisi sınıfı bulunamadı.")

            SistemYoneticisi._dil_servisi_instance = cls()

        return SistemYoneticisi._dil_servisi_instance

    # =========================================================
    # AYAR
    # =========================================================
    def ayarlari_yukle(self) -> dict:
        fn = self._modul_fonksiyonu(
            "app.services.sistem.ayar_servisi",
            "ayarlari_yukle",
        )
        return fn() if callable(fn) else {}

    def ayarlari_kaydet(self, data: dict) -> None:
        fn = self._modul_fonksiyonu(
            "app.services.sistem.ayar_servisi",
            "ayarlari_kaydet",
        )
        if callable(fn):
            fn(data)

    def get_language(self, default: str = "tr") -> str:
        fn = self._modul_fonksiyonu(
            "app.services.sistem.ayar_servisi",
            "get_language",
        )
        if callable(fn):
            try:
                return str(fn(default=default) or default)
            except Exception:
                pass
        return str(default or "tr")

    def set_language(self, code: str) -> None:
        fn = self._modul_fonksiyonu(
            "app.services.sistem.ayar_servisi",
            "set_language",
        )
        if callable(fn):
            fn(code)

    def supported_languages(self) -> list[str]:
        try:
            return self.mevcut_dil_kodlari()
        except Exception:
            fn = self._modul_fonksiyonu(
                "app.services.sistem.ayar_servisi",
                "supported_languages",
            )
            if callable(fn):
                try:
                    return list(fn() or [])
                except Exception:
                    pass
            return []

    def language_supported(self, code: str) -> bool:
        try:
            return self.dil_destekleniyor_mu(code)
        except Exception:
            fn = self._modul_fonksiyonu(
                "app.services.sistem.ayar_servisi",
                "language_supported",
            )
            if callable(fn):
                try:
                    return bool(fn(code))
                except Exception:
                    pass
            return False

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
        fn = self._modul_fonksiyonu(
            "app.services.sistem.ayar_servisi",
            "get_app_state",
        )
        if callable(fn):
            try:
                return fn(default=default)
            except Exception:
                pass
        return dict(default or {})

    def set_app_state(self, state: dict) -> None:
        fn = self._modul_fonksiyonu(
            "app.services.sistem.ayar_servisi",
            "set_app_state",
        )
        if callable(fn):
            fn(state)

    def clear_app_state(self) -> None:
        fn = self._modul_fonksiyonu(
            "app.services.sistem.ayar_servisi",
            "clear_app_state",
        )
        if callable(fn):
            fn()

    # =========================================================
    # GECICI BILDIRIM
    # =========================================================
    def _gecici_bildirim_servisi(self):
        return self._modul_nesnesi(
            "app.services.sistem.gecici_bildirim_servisi",
            "gecici_bildirim_servisi",
        )

    def register_bildirim_layer(self, layer) -> bool:
        servis = self._gecici_bildirim_servisi()
        if servis is None:
            return False

        try:
            return bool(servis.register_layer(layer))
        except Exception:
            return False

    def unregister_bildirim_layer(self) -> None:
        servis = self._gecici_bildirim_servisi()
        if servis is None:
            return

        try:
            servis.unregister_layer()
        except Exception:
            pass

    def bildirim_layer_var_mi(self) -> bool:
        servis = self._gecici_bildirim_servisi()
        if servis is None:
            return False

        try:
            return bool(servis.has_layer())
        except Exception:
            return False

    def bildirim_goster(
        self,
        text: str,
        icon_name: str = "",
        duration: float = 2.4,
        title: str = "",
        tone: str = "info",
        on_tap=None,
    ) -> bool:
        servis = self._gecici_bildirim_servisi()
        if servis is None:
            return False

        try:
            return bool(
                servis.show(
                    text=text,
                    icon_name=icon_name,
                    duration=duration,
                    title=title,
                    tone=tone,
                    on_tap=on_tap,
                )
            )
        except Exception:
            return False

    def bildirim_gizle(self) -> bool:
        servis = self._gecici_bildirim_servisi()
        if servis is None:
            return False

        try:
            return bool(servis.hide())
        except Exception:
            return False

    def bildirimi_aninda_gizle(self) -> bool:
        servis = self._gecici_bildirim_servisi()
        if servis is None:
            return False

        try:
            return bool(servis.hide_immediately())
        except Exception:
            return False

    # =========================================================
    # PREMIUM
    # =========================================================
    def premium_aktif_mi(self) -> bool:
        servis = self._modul_nesnesi(
            "app.services.sistem.premium_servisi",
            "premium_servisi",
        )
        if servis is None:
            return False

        try:
            return bool(servis.premium_aktif_mi())
        except Exception:
            return False
