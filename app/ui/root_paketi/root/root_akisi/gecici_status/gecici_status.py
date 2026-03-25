# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/root/root_akisi/gecici_status/gecici_status.py

ROL:
- Root katmanındaki geçici status gösterim akışını tek modülde toplar
- Özellikle oturum geri yükleme sonrası kısa süreli bilgi mesajı gösterir
- Geçici status süresi dolunca ana duruma geri dönüşü otomatik yapar
- Status action temizleme ve reset event yönetimini merkezi hale getirir
- Runtime tarafında lazy resolve ve cache kullanarak tekrar eden lookup maliyetini azaltır

MİMARİ:
- Bu modül mixin mantığıyla çalışır
- RootWidget içinde kullanılan geçici status helper metodları burada tanımlanır
- Status widget erişimi method/attribute lookup cache ile optimize edilir
- Reset event nesnesi root üzerinde tutulur
- Yeni geçici status çağrısı geldiğinde önceki reset event iptal edilir
- Fail-soft yaklaşım uygulanır; hata UI akışını bozmaz
- Import-level lazy import bu dosyada hedeflenmez; burada runtime lazy resolve + cache uygulanır

DESTEKLENEN AKIŞ:
- Status action varsa temizlenir
- Geçici info status gösterilir
- Belirli süre sonunda status tekrar "Hazır." durumuna döner
- Bekleyen tarama geçişi varsa otomatik reset yapılmaz
- Reset sonrası update check yeniden tetiklenebilir

BEKLENEN ROOT ALANLARI:
- self.status
- self._restore_status_reset_event
- self._pending_scan_ready

BEKLENEN ROOT METODLARI:
- self.set_status_info(...)
- self._m(...)
- self._check_update_from_endpoint(...)

NOTLAR:
- Bu modül sadece geçici bilgi mesajı akışına odaklanır
- Toast / popup üretmez
- Disk yazımı yapmaz
- Kalıcı status mantığı içermez
- Status widget API'si değişirse cache temizlenerek yeniden resolve edilebilir

SURUM: 1
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

from kivy.clock import Clock


class RootGeciciStatusMixin:
    """
    Root katmanında geçici status davranışlarını sağlayan mixin.
    """

    # =========================================================
    # CACHE
    # =========================================================
    def _ensure_gecici_status_cache(self) -> None:
        """
        Geçici status yardımcı cache alanlarını hazırlar.
        """
        try:
            if not hasattr(self, "_gecici_status_cache"):
                self._gecici_status_cache = {}
        except Exception:
            pass

    def _gecici_status_cache_temizle(self) -> None:
        """
        Geçici status yardımcı cache alanlarını temizler.
        """
        try:
            self._gecici_status_cache = {}
        except Exception:
            pass

    def _cache_get(self, key: str, default=None):
        """
        Cache içinden güvenli biçimde değer alır.
        """
        try:
            self._ensure_gecici_status_cache()
            return self._gecici_status_cache.get(key, default)
        except Exception:
            return default

    def _cache_set(self, key: str, value) -> None:
        """
        Cache içine güvenli biçimde değer yazar.
        """
        try:
            self._ensure_gecici_status_cache()
            self._gecici_status_cache[key] = value
        except Exception:
            pass

    # =========================================================
    # INTERNAL HELPERS
    # =========================================================
    def _safe_getattr(self, name: str, default=None):
        """
        Root üzerinde güvenli getattr çağrısı yapar.
        """
        try:
            return getattr(self, name, default)
        except Exception:
            return default

    def _resolve_status_method(self, method_name: str):
        """
        Status widget üzerinde metod arar ve cache'ler.

        Args:
            method_name: Aranacak metod adı.

        Returns:
            callable | None
        """
        status = self._safe_getattr("status", None)
        if status is None:
            return None

        try:
            object_id = id(status)
            cache_key = f"status_method::{object_id}::{method_name}"
            cached = self._cache_get(cache_key, None)
            if cached is not None:
                return cached
        except Exception:
            cache_key = None

        bulunan = None
        try:
            method = getattr(status, method_name, None)
            if callable(method):
                bulunan = method
        except Exception:
            bulunan = None

        try:
            if cache_key is not None and bulunan is not None:
                self._cache_set(cache_key, bulunan)
        except Exception:
            pass

        return bulunan

    def _resolve_root_method(self, method_name: str):
        """
        Root üzerinde metod arar ve cache'ler.

        Args:
            method_name: Aranacak metod adı.

        Returns:
            callable | None
        """
        try:
            object_id = id(self)
            cache_key = f"root_method::{object_id}::{method_name}"
            cached = self._cache_get(cache_key, None)
            if cached is not None:
                return cached
        except Exception:
            cache_key = None

        bulunan = None
        try:
            method = getattr(self, method_name, None)
            if callable(method):
                bulunan = method
        except Exception:
            bulunan = None

        try:
            if cache_key is not None and bulunan is not None:
                self._cache_set(cache_key, bulunan)
        except Exception:
            pass

        return bulunan

    def _resolve_root_bool_attr(self, attr_name: str, default=False) -> bool:
        """
        Root üzerinde bool benzeri alanı güvenli biçimde çözer.

        Args:
            attr_name: Alan adı.
            default: Alan okunamazsa varsayılan değer.

        Returns:
            bool
        """
        try:
            return bool(self._safe_getattr(attr_name, default))
        except Exception:
            return bool(default)

    # =========================================================
    # EVENT HELPERS
    # =========================================================
    def _cancel_restore_status_reset_event(self) -> None:
        """
        Varsa bekleyen geçici status reset event'ini iptal eder.
        """
        try:
            event = self._safe_getattr("_restore_status_reset_event", None)
            if event is not None and hasattr(event, "cancel"):
                event.cancel()
        except Exception:
            pass

        try:
            self._restore_status_reset_event = None
        except Exception:
            pass

    def _schedule_restore_status_reset(self, callback, duration: float) -> None:
        """
        Geçici status reset event'ini planlar.

        Args:
            callback: Süre dolunca çalışacak callback.
            duration: Bekleme süresi.
        """
        try:
            self._restore_status_reset_event = Clock.schedule_once(
                callback,
                float(duration),
            )
        except Exception:
            try:
                self._restore_status_reset_event = None
            except Exception:
                pass

    # =========================================================
    # STATUS HELPERS
    # =========================================================
    def _clear_status_action_if_available(self) -> None:
        """
        Status widget üzerinde clear_action varsa çağırır.
        """
        try:
            clear_action = self._resolve_status_method("clear_action")
            if callable(clear_action):
                clear_action()
        except Exception:
            pass

    def _set_status_info_cached(self, message: str, icon_name: str) -> bool:
        """
        Root üzerindeki set_status_info metodunu cache ile çağırır.

        Args:
            message: Gösterilecek mesaj.
            icon_name: İkon adı.

        Returns:
            bool: Başarılıysa True
        """
        try:
            set_status_info = self._resolve_root_method("set_status_info")
            if callable(set_status_info):
                set_status_info(str(message or ""), icon_name)
                return True
        except Exception:
            pass

        return False

    def _metin_al(self, anahtar: str, default: str) -> str:
        """
        Root üzerindeki _m metodunu cache ile çağırır.

        Args:
            anahtar: Çeviri anahtarı.
            default: Varsayılan metin.

        Returns:
            str
        """
        try:
            m = self._resolve_root_method("_m")
            if callable(m):
                return str(m(anahtar, default) or default or anahtar)
        except Exception:
            pass

        return str(default or anahtar)

    def _trigger_update_check_if_available(self, delay: float = 0.10) -> None:
        """
        Root üzerindeki update check metodunu gecikmeli olarak tetikler.
        """
        try:
            check_method = self._resolve_root_method("_check_update_from_endpoint")
            if callable(check_method):
                Clock.schedule_once(check_method, float(delay))
        except Exception:
            pass

    # =========================================================
    # GECICI STATUS
    # =========================================================
    def _show_temporary_restore_status(
        self,
        message: str,
        icon_name: str = "onaylandi.png",
        duration: float = 3.5,
    ) -> None:
        """
        Geçici geri yükleme status bilgisini gösterir ve süre sonunda sıfırlar.

        Akış:
        - Önceki reset event iptal edilir
        - Status action temizlenir
        - Geçici bilgi mesajı gösterilir
        - duration sonunda tekrar "Hazır." bilgisine dönülür
        - Bekleyen scan transition varsa reset uygulanmaz

        Args:
            message: Gösterilecek geçici mesaj.
            icon_name: Status ikon adı.
            duration: Mesajın görünme süresi.
        """
        self._cancel_restore_status_reset_event()
        self._clear_status_action_if_available()

        try:
            ok = self._set_status_info_cached(
                str(message or self._metin_al("session_restored", "Oturum geri yüklendi.")),
                icon_name,
            )
            if not ok:
                return
        except Exception:
            return

        def _reset_status(*_args):
            try:
                self._restore_status_reset_event = None
            except Exception:
                pass

            try:
                if self._resolve_root_bool_attr("_pending_scan_ready", False):
                    return
            except Exception:
                pass

            try:
                self._set_status_info_cached(
                    self._metin_al("app_ready", "Hazır."),
                    "onaylandi.png",
                )
            except Exception:
                pass

            try:
                self._trigger_update_check_if_available(delay=0.10)
            except Exception:
                pass

        self._schedule_restore_status_reset(_reset_status, float(duration))