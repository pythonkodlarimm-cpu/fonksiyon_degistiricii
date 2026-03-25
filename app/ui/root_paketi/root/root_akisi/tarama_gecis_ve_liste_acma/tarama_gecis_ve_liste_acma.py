# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/root/root_akisi/tarama_gecis_ve_liste_acma/tarama_gecis_ve_liste_acma.py

ROL:
- Root katmanında tarama tamamlandıktan sonra doğal geçiş akışını yönetir
- Tarama sonucu ile fonksiyon listesi açılışı arasına aksiyonlu geçiş katmanı ekler
- Geçiş reklamı hazırsa gösterir, değilse listeyi direkt açar
- Bekleyen tarama sonucu bilgisini root üzerinde tutar ve temizler
- Status CTA oluşturur, kullanıcıyı "Listeyi Aç" aksiyonuna yönlendirir
- Fonksiyon listesi doldurma, listeye scroll etme ve geçiş sonrası status güncellemesini yönetir
- Runtime tarafında lazy resolve ve cache kullanarak tekrar eden lookup maliyetini azaltır

MİMARİ:
- Bu modül mixin mantığıyla çalışır
- Import-level lazy import bu dosyada hedeflenmez; burada runtime lazy resolve + cache uygulanır
- Services çağrıları doğrudan import edilmez, root üzerindeki self.services üzerinden çözülür
- Status widget method çözümlemeleri cache içine alınır
- Root method çözümlemeleri cache içine alınır
- Fail-soft yaklaşım uygulanır; reklam, status ya da liste açma adımlarındaki hata root'u çökertmez

DESTEKLENEN ROOT ALANLARI:
- self.services
- self.status
- self.items
- self.function_list
- self._pending_scan_result
- self._pending_scan_item_count
- self._pending_scan_display_name
- self._pending_scan_ready
- self._scan_transition_busy

BEKLENEN ROOT METODLARI:
- self._m(...)
- self.set_status_success(...)
- self.set_status_info(...)
- self._scroll_to_function_list(...)
- self._check_update_from_endpoint(...)
- self._ensure_banner_visibility(...)
- self._try_preload_interstitial(...)

BEKLENEN SERVICES API:
- gecis_reklami_hazir_mi()
- gecis_reklami_goster(sonrasi_callback=...)

NOTLAR:
- Bu modül yalnızca tarama geçişi ve liste açma akışına odaklanır
- Tarama işini yapmaz; sadece tarama sonrası geçişi yönetir
- Geçiş reklamı gösterilemezse liste doğrudan açılır
- CTA temizleme işlemi status widget üzerinde clear_action varsa yapılır

SURUM: 1
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

import traceback

from kivy.clock import Clock


class RootTaramaGecisVeListeAcmaMixin:
    """
    Root katmanında tarama -> geçiş -> liste açma akışını yöneten mixin.
    """

    # =========================================================
    # CACHE
    # =========================================================
    def _ensure_tarama_gecis_cache(self) -> None:
        """
        Tarama geçiş akışı için yardımcı cache alanlarını hazırlar.
        """
        try:
            if not hasattr(self, "_tarama_gecis_cache"):
                self._tarama_gecis_cache = {}
        except Exception:
            pass

    def _tarama_gecis_cache_temizle(self) -> None:
        """
        Tarama geçiş akışı cache alanlarını temizler.
        """
        try:
            self._tarama_gecis_cache = {}
        except Exception:
            pass

    def _tarama_cache_get(self, key: str, default=None):
        """
        Cache içinden güvenli biçimde değer okur.
        """
        try:
            self._ensure_tarama_gecis_cache()
            return self._tarama_gecis_cache.get(key, default)
        except Exception:
            return default

    def _tarama_cache_set(self, key: str, value) -> None:
        """
        Cache içine güvenli biçimde değer yazar.
        """
        try:
            self._ensure_tarama_gecis_cache()
            self._tarama_gecis_cache[key] = value
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

    def _resolve_root_method(self, method_name: str):
        """
        Root üzerindeki callable metodu lazy resolve eder ve cache'ler.

        Args:
            method_name: Çözümlenecek method adı.

        Returns:
            callable | None
        """
        cache_key = None

        try:
            cache_key = f"root_method::{id(self)}::{method_name}"
            cached = self._tarama_cache_get(cache_key, None)
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
                self._tarama_cache_set(cache_key, bulunan)
        except Exception:
            pass

        return bulunan

    def _resolve_services(self):
        """
        Root üzerindeki services nesnesini lazy resolve eder ve cache'ler.
        """
        try:
            services = self._tarama_cache_get("services_obj", None)
            if services is not None:
                return services
        except Exception:
            pass

        try:
            services = self._safe_getattr("services", None)
            if services is not None:
                self._tarama_cache_set("services_obj", services)
            return services
        except Exception:
            return None

    def _resolve_services_method(self, method_name: str):
        """
        Services üzerindeki callable metodu lazy resolve eder ve cache'ler.

        Args:
            method_name: Çözümlenecek method adı.

        Returns:
            callable | None
        """
        services = self._resolve_services()
        if services is None:
            return None

        cache_key = None

        try:
            cache_key = f"services_method::{id(services)}::{method_name}"
            cached = self._tarama_cache_get(cache_key, None)
            if cached is not None:
                return cached
        except Exception:
            cache_key = None

        bulunan = None
        try:
            method = getattr(services, method_name, None)
            if callable(method):
                bulunan = method
        except Exception:
            bulunan = None

        try:
            if cache_key is not None and bulunan is not None:
                self._tarama_cache_set(cache_key, bulunan)
        except Exception:
            pass

        return bulunan

    def _resolve_status_method(self, method_name: str):
        """
        Status widget üzerindeki callable metodu lazy resolve eder ve cache'ler.

        Args:
            method_name: Çözümlenecek method adı.

        Returns:
            callable | None
        """
        status = self._safe_getattr("status", None)
        if status is None:
            return None

        cache_key = None

        try:
            cache_key = f"status_method::{id(status)}::{method_name}"
            cached = self._tarama_cache_get(cache_key, None)
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
                self._tarama_cache_set(cache_key, bulunan)
        except Exception:
            pass

        return bulunan

    def _m_cached(self, anahtar: str, default: str = "") -> str:
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

    def _root_call_noargs(self, method_name: str) -> bool:
        """
        Root üzerinde argümansız method çağırmayı dener.

        Args:
            method_name: Method adı.

        Returns:
            bool
        """
        try:
            method = self._resolve_root_method(method_name)
            if callable(method):
                method()
                return True
        except Exception:
            pass
        return False

    def _root_call_later(self, method_name: str, delay: float) -> None:
        """
        Root üzerindeki methodu gecikmeli çağırmayı planlar.

        Args:
            method_name: Method adı.
            delay: Gecikme süresi.
        """
        try:
            method = self._resolve_root_method(method_name)
            if callable(method):
                Clock.schedule_once(method, float(delay))
        except Exception:
            pass

    def _root_set_status_success(self, message: str) -> bool:
        """
        Root üzerindeki set_status_success metodunu çağırır.

        Args:
            message: Status mesajı.

        Returns:
            bool
        """
        try:
            method = self._resolve_root_method("set_status_success")
            if callable(method):
                method(str(message or ""))
                return True
        except Exception:
            pass
        return False

    def _root_set_status_info(self, message: str, icon_name: str) -> bool:
        """
        Root üzerindeki set_status_info metodunu çağırır.

        Args:
            message: Status mesajı.
            icon_name: İkon adı.

        Returns:
            bool
        """
        try:
            method = self._resolve_root_method("set_status_info")
            if callable(method):
                method(str(message or ""), str(icon_name or ""))
                return True
        except Exception:
            pass
        return False

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

    def _set_status_action_if_available(
        self,
        text: str,
        button_text: str,
        callback,
        icon_name: str,
        tone: str,
    ) -> bool:
        """
        Status widget üzerinde set_action varsa çağırır.

        Returns:
            bool
        """
        try:
            set_action = self._resolve_status_method("set_action")
            if callable(set_action):
                set_action(
                    text=str(text or ""),
                    button_text=str(button_text or ""),
                    callback=callback,
                    icon_name=str(icon_name or ""),
                    tone=str(tone or ""),
                )
                return True
        except Exception:
            pass
        return False

    def _services_bool_call(self, method_name: str, default: bool = False) -> bool:
        """
        Services üzerindeki bool dönen methodu güvenli biçimde çağırır.
        """
        try:
            method = self._resolve_services_method(method_name)
            if callable(method):
                return bool(method())
        except Exception:
            pass
        return bool(default)

    def _services_gecis_reklami_goster(self, sonrasi_callback) -> bool:
        """
        Services üzerinden geçiş reklamı gösterme çağrısını yapar.

        Args:
            sonrasi_callback: Reklam sonrası callback.

        Returns:
            bool
        """
        try:
            method = self._resolve_services_method("gecis_reklami_goster")
            if callable(method):
                return bool(method(sonrasi_callback=sonrasi_callback))
        except Exception:
            pass
        return False

    # =========================================================
    # ROOT STATE HELPERS
    # =========================================================
    def _pending_scan_ready_get(self) -> bool:
        """
        Bekleyen tarama geçişi var mı bilgisini okur.
        """
        try:
            return bool(self._safe_getattr("_pending_scan_ready", False))
        except Exception:
            return False

    def _scan_transition_busy_get(self) -> bool:
        """
        Tarama geçişi meşgul mü bilgisini okur.
        """
        try:
            return bool(self._safe_getattr("_scan_transition_busy", False))
        except Exception:
            return False

    def _scan_transition_busy_set(self, value: bool) -> None:
        """
        Tarama geçişi meşgul alanını günceller.
        """
        try:
            self._scan_transition_busy = bool(value)
        except Exception:
            pass

    # =========================================================
    # TARAMA HAZIR
    # =========================================================
    def _on_scan_transition_ready(
        self,
        item_count: int = 0,
        display_name: str = "",
    ) -> None:
        """
        Tarama tamamlandıktan sonra geçiş akışını hazırlar.

        Args:
            item_count: Bulunan fonksiyon sayısı.
            display_name: Tarama yapılan dosyanın görüntü adı.
        """
        try:
            self._pending_scan_item_count = int(item_count or 0)
        except Exception:
            self._pending_scan_item_count = 0

        try:
            self._pending_scan_display_name = str(display_name or "").strip()
        except Exception:
            self._pending_scan_display_name = ""

        try:
            self._pending_scan_ready = True
        except Exception:
            pass

        try:
            self._root_call_noargs("_clear_update_cta")
        except Exception:
            pass

        try:
            self._root_call_noargs("_try_preload_interstitial")
        except Exception:
            pass

        mesaj = self._m_cached(
            "scan_completed_with_count",
            f"Tarama tamamlandı. {self._safe_getattr('_pending_scan_item_count', 0)} fonksiyon bulundu.",
        )

        if mesaj == "scan_completed_with_count":
            mesaj = (
                f"{self._m_cached('scan_completed', 'Tarama tamamlandı.')} "
                f"{self._safe_getattr('_pending_scan_item_count', 0)} "
                f"{self._m_cached('function_found_count_suffix', 'fonksiyon bulundu.')}"
            )

        try:
            ok = self._set_status_action_if_available(
                text=mesaj,
                button_text=self._m_cached("open_list", "Listeyi Aç"),
                callback=self.continue_after_scan_transition,
                icon_name="onaylandi.png",
                tone="success",
            )
            if not ok:
                self._root_set_status_success(
                    mesaj
                    + " "
                    + self._m_cached(
                        "continue_to_open_list",
                        "Listeyi açmak için devam edin.",
                    )
                )
        except Exception:
            self._root_set_status_success(
                mesaj
                + " "
                + self._m_cached(
                    "continue_to_open_list",
                    "Listeyi açmak için devam edin.",
                )
            )

        print(
            "[ROOT] Tarama geçiş aşaması hazırlandı | "
            f"item_count={self._safe_getattr('_pending_scan_item_count', 0)} "
            f"display_name={self._safe_getattr('_pending_scan_display_name', '')}"
        )

    # =========================================================
    # CLEAR STATE
    # =========================================================
    def _clear_scan_transition_state(self) -> None:
        """
        Bekleyen tarama geçiş state alanlarını temizler.
        """
        try:
            self._pending_scan_result = None
        except Exception:
            pass

        try:
            self._pending_scan_item_count = 0
        except Exception:
            pass

        try:
            self._pending_scan_display_name = ""
        except Exception:
            pass

        try:
            self._pending_scan_ready = False
        except Exception:
            pass

        try:
            self._scan_transition_busy = False
        except Exception:
            pass

        try:
            self._clear_status_action_if_available()
        except Exception:
            pass

    # =========================================================
    # LIST APPLY / OPEN
    # =========================================================
    def _apply_function_list_after_transition(self) -> None:
        """
        Geçiş sonrası fonksiyon listesini doldurur.
        """
        try:
            function_list = self._safe_getattr("function_list", None)
            items = list(self._safe_getattr("items", []) or [])

            if function_list is not None and hasattr(function_list, "set_items"):
                function_list.set_items(items)
                print(
                    "[ROOT] Fonksiyon listesi geçiş sonrası dolduruldu. "
                    f"item_count={len(items)}"
                )
        except Exception:
            print("[ROOT] Fonksiyon listesi geçiş sonrası doldurulamadı.")
            print(traceback.format_exc())

    def _open_function_list_after_transition(self) -> None:
        """
        Geçiş tamamlandıktan sonra fonksiyon listesini açar ve UI durumunu günceller.
        """
        try:
            self._apply_function_list_after_transition()
            self._clear_scan_transition_state()

            try:
                scroll_method = self._resolve_root_method("_scroll_to_function_list")
                if callable(scroll_method):
                    Clock.schedule_once(lambda *_: scroll_method(), 0.10)
            except Exception:
                pass

            self._root_set_status_success(
                self._m_cached("list_opened", "Fonksiyon listesi açıldı.")
            )
            print("[ROOT] Fonksiyon listesi geçiş sonrası açıldı.")

            self._root_call_later("_check_update_from_endpoint", 0.40)

            try:
                self._root_call_later("_ensure_banner_visibility", 0.30)
                self._root_call_later("_ensure_banner_visibility", 1.00)
            except Exception:
                pass

        except Exception:
            print("[ROOT] Fonksiyon listesi açılamadı.")
            print(traceback.format_exc())

    # =========================================================
    # CONTINUE / CANCEL
    # =========================================================
    def continue_after_scan_transition(self) -> bool:
        """
        Bekleyen tarama geçişini devam ettirir.

        Akış:
        - Bekleyen geçiş yoksa False
        - Zaten çalışıyorsa False
        - Reklam hazırsa reklamı gösterir
        - Reklam gösterilemezse listeyi direkt açar

        Returns:
            bool
        """
        if not self._pending_scan_ready_get():
            print("[ROOT] Bekleyen tarama geçişi yok.")
            return False

        if self._scan_transition_busy_get():
            print("[ROOT] Tarama geçişi zaten işleniyor.")
            return False

        self._scan_transition_busy_set(True)

        try:
            if self._services_bool_call("gecis_reklami_hazir_mi", default=False):
                print("[ROOT] Geçiş reklamı hazır. Gösteriliyor...")
                gosterildi = self._services_gecis_reklami_goster(
                    sonrasi_callback=self._open_function_list_after_transition,
                )

                if gosterildi:
                    return True

            print("[ROOT] Geçiş reklamı hazır değil veya gösterilemedi. Direkt açılıyor.")
            self._open_function_list_after_transition()
            return True

        except Exception:
            print("[ROOT] Geçiş reklamı akışı başarısız. Direkt açılıyor.")
            print(traceback.format_exc())
            self._open_function_list_after_transition()
            return False

    def cancel_scan_transition(self) -> None:
        """
        Bekleyen tarama geçişini iptal eder ve root'u hazır durumuna döndürür.
        """
        self._clear_scan_transition_state()

        try:
            function_list = self._safe_getattr("function_list", None)
            if function_list is not None and hasattr(function_list, "clear_all"):
                function_list.clear_all()
        except Exception:
            pass

        self._root_set_status_info(
            self._m_cached("app_ready", "Hazır."),
            "onaylandi.png",
        )
        self._root_call_later("_check_update_from_endpoint", 0.10)

        try:
            self._root_call_later("_ensure_banner_visibility", 0.25)
        except Exception:
            pass