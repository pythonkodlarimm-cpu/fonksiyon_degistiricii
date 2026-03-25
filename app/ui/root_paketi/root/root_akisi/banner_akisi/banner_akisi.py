# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/root/root_akisi/banner_akisi/banner_akisi.py

ROL:
- Root katmanında banner reklam başlatma ve görünürlük doğrulama akışını yönetir
- Android tarafında banner reklamın güvenli ve gecikmeli biçimde başlatılmasını sağlar
- Banner görünmüyorsa kontrollü retry akışı uygular
- ServicesYoneticisi üzerindeki banner API erişimlerini lazy resolve eder
- Method ve sonuç erişimlerinde runtime cache kullanarak tekrar eden lookup maliyetini azaltır
- Hata ve kritik debug bilgilerini ekranda kopyalanabilir popup ile gösterebilir
- Services çağrılarında sessiz yutulan hataları görünür hale getirir

MİMARİ:
- Bu modül mixin mantığıyla çalışır
- Import-level lazy import bu dosyada hedeflenmez; burada runtime lazy resolve + cache uygulanır
- Services katmanı doğrudan import edilmez, root üzerindeki self.services üzerinden erişilir
- Banner API method çözümleme sonuçları cache içine alınır
- Retry sayacı root alanları üzerinden yönetilir
- UI akışı fail-soft tasarlanmıştır; reklam servisi hata verse bile root çökmemelidir
- Debug popup desteği bu modül içinde tutulur; root.py şişirilmez
- Services method resolve ve call aşamalarında hata popup desteği vardır
- Mixin çakışmalarını önlemek için benzersiz helper method adları kullanılır

DESTEKLENEN ROOT ALANLARI:
- self.services
- self._banner_started
- self._banner_retry_count
- self._banner_retry_max

BEKLENEN ROOT / ENV:
- kivy.utils.platform
- kivy.clock.Clock

BEKLENEN SERVICES API:
- banner_gosteriliyor_mu()
- banner_planlandi_mi()
- banner_goster_gecikmeli(delay=...)
- reklam_modu_etiketi()

NOTLAR:
- Bu modül sadece banner akışına odaklanır
- Banner görünürlüğü kontrol edilir, planlı durumlar yeniden gözlenir
- Banner hiç görünmezse belirli limit dahilinde retry yapılır
- Android dışında banner akışı çalıştırılmaz
- Popup debug sadece gerektiğinde gösterilir
- İstenirse _DEBUG_POPUP_AKTIF değeri False yapılarak susturulabilir
- Amaç mevcut davranışı bozmadan gerçek hatayı görünür hale getirmektir

SURUM: 4
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

import traceback

from kivy.clock import Clock
from kivy.utils import platform


_DEBUG_POPUP_AKTIF = True


class RootBannerAkisiMixin:
    """
    Root katmanında banner reklam akışını yöneten mixin.
    """

    # =========================================================
    # CACHE
    # =========================================================
    def _ensure_banner_cache(self) -> None:
        try:
            if not hasattr(self, "_banner_akisi_cache"):
                self._banner_akisi_cache = {}
        except Exception:
            pass

    def _banner_cache_temizle(self) -> None:
        try:
            self._banner_akisi_cache = {}
        except Exception:
            pass

    def _banner_cache_get(self, key: str, default=None):
        try:
            self._ensure_banner_cache()
            return self._banner_akisi_cache.get(key, default)
        except Exception:
            return default

    def _banner_cache_set(self, key: str, value) -> None:
        try:
            self._ensure_banner_cache()
            self._banner_akisi_cache[key] = value
        except Exception:
            pass

    # =========================================================
    # INTERNAL HELPERS
    # =========================================================
    def _banner_safe_getattr(self, name: str, default=None):
        try:
            return getattr(self, name, default)
        except Exception:
            return default

    def _banner_resolve_services(self):
        try:
            services = self._banner_cache_get("services_obj", None)
            if services is not None:
                return services
        except Exception:
            pass

        try:
            services = self._banner_safe_getattr("services", None)
            if services is not None:
                self._banner_cache_set("services_obj", services)
            return services
        except Exception:
            return None

    def _banner_resolve_services_method(self, method_name: str):
        services = self._banner_resolve_services()
        if services is None:
            self._banner_popup_debug(
                "services nesnesi bulunamadı.",
                title="Banner Services Hatası",
            )
            return None

        cache_key = None

        try:
            cache_key = f"services_method::{id(services)}::{method_name}"
            cached = self._banner_cache_get(cache_key, None)
            if cached is not None:
                return cached
        except Exception:
            cache_key = None

        bulunan = None
        try:
            method = getattr(services, method_name, None)
            if callable(method):
                bulunan = method
            else:
                self._banner_popup_debug(
                    f"Services üzerinde method bulunamadı:\n\n{method_name}",
                    title="Banner Method Bulunamadı",
                )
        except Exception:
            self._banner_popup_debug(
                traceback.format_exc(),
                title=f"Method Resolve Hatası: {method_name}",
            )
            bulunan = None

        try:
            if cache_key is not None and bulunan is not None:
                self._banner_cache_set(cache_key, bulunan)
        except Exception:
            pass

        return bulunan

    def _banner_services_bool_call(
        self,
        method_name: str,
        default: bool = False,
    ) -> bool:
        try:
            method = self._banner_resolve_services_method(method_name)
            if callable(method):
                return bool(method())
        except Exception:
            self._banner_popup_debug(
                traceback.format_exc(),
                title=f"Services Bool Call Hatası: {method_name}",
            )
        return bool(default)

    def _banner_services_text_call(
        self,
        method_name: str,
        default: str = "",
    ) -> str:
        try:
            method = self._banner_resolve_services_method(method_name)
            if callable(method):
                sonuc = method()
                return str(sonuc or default)
        except Exception:
            self._banner_popup_debug(
                traceback.format_exc(),
                title=f"Services Text Call Hatası: {method_name}",
            )
        return str(default or "")

    def _banner_services_show_delayed(self, delay: float = 1.5):
        try:
            method = self._banner_resolve_services_method(
                "banner_goster_gecikmeli"
            )
            if callable(method):
                return method(delay=float(delay))

            self._banner_popup_debug(
                "banner_goster_gecikmeli methodu callable değil veya bulunamadı.",
                title="Banner Delayed Call Hatası",
            )
        except Exception:
            self._banner_popup_debug(
                traceback.format_exc(),
                title="banner_goster_gecikmeli Exception",
            )
        return None

    # =========================================================
    # DEBUG / POPUP
    # =========================================================
    def _banner_debug(self, message: str) -> None:
        try:
            print("[ROOT_BANNER]", str(message))
        except Exception:
            pass

    def _banner_popup_debug(self, text: str, title: str = "Banner Debug") -> None:
        if not _DEBUG_POPUP_AKTIF:
            return

        try:
            from kivy.uix.popup import Popup
            from kivy.uix.boxlayout import BoxLayout
            from kivy.uix.textinput import TextInput
            from kivy.uix.button import Button
            from kivy.core.clipboard import Clipboard
            from kivy.metrics import dp

            def _ui(_dt):
                try:
                    content = BoxLayout(
                        orientation="vertical",
                        spacing=dp(8),
                        padding=dp(8),
                    )

                    txt = TextInput(
                        text=str(text or ""),
                        readonly=True,
                        multiline=True,
                        size_hint=(1, 1),
                    )

                    buton_satiri = BoxLayout(
                        orientation="horizontal",
                        size_hint=(1, None),
                        height=dp(48),
                        spacing=dp(8),
                    )

                    btn_kopyala = Button(text="Kopyala")
                    btn_kapat = Button(text="Kapat")

                    popup_ref = {"popup": None}

                    def _copy(*_args):
                        try:
                            Clipboard.copy(txt.text or "")
                        except Exception:
                            pass

                    def _close(*_args):
                        try:
                            if popup_ref["popup"] is not None:
                                popup_ref["popup"].dismiss()
                        except Exception:
                            pass

                    btn_kopyala.bind(on_release=_copy)
                    btn_kapat.bind(on_release=_close)

                    buton_satiri.add_widget(btn_kopyala)
                    buton_satiri.add_widget(btn_kapat)

                    content.add_widget(txt)
                    content.add_widget(buton_satiri)

                    popup = Popup(
                        title=str(title or "Banner Debug"),
                        content=content,
                        size_hint=(0.95, 0.82),
                        auto_dismiss=True,
                    )
                    popup_ref["popup"] = popup
                    popup.open()

                except Exception:
                    self._banner_debug("Banner popup debug UI oluşturulamadı.")
                    self._banner_debug(traceback.format_exc())

            Clock.schedule_once(_ui, 0)

        except Exception:
            self._banner_debug("Banner popup debug gösterilemedi.")
            self._banner_debug(traceback.format_exc())

    def _banner_debug_state_popup(self, title: str, extra_text: str = "") -> None:
        try:
            satirlar = [
                f"platform = {platform}",
                "banner_gosteriliyor_mu = "
                f"{self._banner_services_bool_call('banner_gosteriliyor_mu', default=False)}",
                "banner_planlandi_mi = "
                f"{self._banner_services_bool_call('banner_planlandi_mi', default=False)}",
                "reklam_modu_etiketi = "
                f"{self._banner_services_text_call('reklam_modu_etiketi', default='')}",
                f"_banner_started = {bool(self._banner_safe_getattr('_banner_started', False))}",
                f"_banner_retry_count = {self._banner_retry_count_get()}",
                f"_banner_retry_max = {self._banner_retry_max_get()}",
            ]

            if extra_text:
                satirlar.append("")
                satirlar.append(str(extra_text))

            self._banner_popup_debug("\n".join(satirlar), title=title)
        except Exception:
            pass

    # =========================================================
    # ROOT STATE HELPERS
    # =========================================================
    def _banner_started_set(self, value: bool) -> None:
        try:
            self._banner_started = bool(value)
        except Exception:
            pass

    def _banner_retry_count_get(self) -> int:
        try:
            return int(self._banner_safe_getattr("_banner_retry_count", 0) or 0)
        except Exception:
            return 0

    def _banner_retry_count_set(self, value: int) -> None:
        try:
            self._banner_retry_count = int(value or 0)
        except Exception:
            pass

    def _banner_retry_max_get(self) -> int:
        try:
            return int(self._banner_safe_getattr("_banner_retry_max", 0) or 0)
        except Exception:
            return 0

    # =========================================================
    # BANNER VISIBILITY CHECK
    # =========================================================
    def _ensure_banner_visibility(self, *_args) -> None:
        try:
            if platform != "android":
                self._banner_debug(
                    f"Banner görünürlük kontrolü atlandı. Platform={platform}"
                )
                return

            gosteriliyor = self._banner_services_bool_call(
                "banner_gosteriliyor_mu",
                default=False,
            )
            planlandi = self._banner_services_bool_call(
                "banner_planlandi_mi",
                default=False,
            )

            if gosteriliyor:
                self._banner_started_set(True)
                self._banner_debug("Banner görünür durumda.")
                return

            if planlandi:
                self._banner_debug(
                    "Banner hâlâ planlı durumda, biraz daha beklenecek."
                )
                Clock.schedule_once(self._ensure_banner_visibility, 1.0)
                return

            self._banner_debug("Banner görünür değil. Yeniden başlatma denenecek.")
            self._banner_started_set(False)
            self._schedule_banner_retry(0.8)

        except Exception:
            self._banner_debug("_ensure_banner_visibility başarısız.")
            self._banner_debug(traceback.format_exc())
            self._banner_popup_debug(
                traceback.format_exc(),
                title="Banner Visibility Hatası",
            )

    # =========================================================
    # START BANNER
    # =========================================================
    def _try_start_banner(self, *_args) -> None:
        self._banner_debug("_try_start_banner çağrıldı.")

        if platform != "android":
            self._banner_debug(
                f"Banner başlatılmadı. Platform android değil: {platform}"
            )
            self._banner_debug_state_popup(
                "Banner Başlatılmadı",
                extra_text="Platform android olmadığı için akış çalıştırılmadı.",
            )
            return

        try:
            if self._banner_services_bool_call(
                "banner_gosteriliyor_mu",
                default=False,
            ):
                self._banner_started_set(True)
                self._banner_debug("Banner zaten görünür durumda.")
                return
        except Exception:
            pass

        try:
            if self._banner_services_bool_call(
                "banner_planlandi_mi",
                default=False,
            ):
                self._banner_debug("Banner zaten planlanmış durumda.")
                Clock.schedule_once(self._ensure_banner_visibility, 1.0)
                return
        except Exception:
            pass

        retry_count = self._banner_retry_count_get()
        retry_max = self._banner_retry_max_get()

        if retry_count >= retry_max:
            self._banner_debug(
                f"Banner başlatma deneme limiti doldu: {retry_count}/{retry_max}"
            )
            self._banner_debug_state_popup(
                "Banner Retry Limiti Doldu",
                extra_text=f"retry_count={retry_count}\nretry_max={retry_max}",
            )
            return

        retry_count += 1
        self._banner_retry_count_set(retry_count)

        self._banner_debug(
            f"Banner başlatma denemesi: {retry_count}/{retry_max}"
        )

        try:
            self._banner_debug(
                "ServicesYoneticisi üzerinden banner_goster_gecikmeli çağrılıyor..."
            )
            sonuc = self._banner_services_show_delayed(delay=1.5)

            self._banner_debug(
                f"banner_goster_gecikmeli sonucu = {sonuc!r}"
            )

            if sonuc is True:
                reklam_modu = self._banner_services_text_call(
                    "reklam_modu_etiketi",
                    "",
                )
                self._banner_debug(
                    f"Banner gösterimi planlandı. Mod={reklam_modu}"
                )
                Clock.schedule_once(self._ensure_banner_visibility, 2.2)
                Clock.schedule_once(self._ensure_banner_visibility, 4.0)
                return

            self._banner_debug(
                "Banner yöneticisi True dönmedi. Tekrar denenecek."
            )
            self._banner_debug_state_popup(
                "Banner Servis Sonucu Beklenenden Farklı",
                extra_text=f"banner_goster_gecikmeli sonucu = {sonuc!r}",
            )
            self._schedule_banner_retry(2.0)

        except Exception:
            self._banner_debug(
                "AdMob banner services yöneticisi üzerinden başlatılamadı."
            )
            self._banner_debug(traceback.format_exc())
            self._banner_popup_debug(
                traceback.format_exc(),
                title="Banner Start Hatası",
            )
            self._schedule_banner_retry(2.0)

    # =========================================================
    # RETRY
    # =========================================================
    def _schedule_banner_retry(self, delay: float = 2.0) -> None:
        try:
            if platform != "android":
                self._banner_debug(
                    f"Retry atlandı. Platform android değil: {platform}"
                )
                return

            try:
                if self._banner_services_bool_call(
                    "banner_gosteriliyor_mu",
                    default=False,
                ):
                    self._banner_started_set(True)
                    self._banner_debug("Retry planlanmadı. Banner zaten görünür.")
                    return
            except Exception:
                pass

            retry_count = self._banner_retry_count_get()
            retry_max = self._banner_retry_max_get()

            if retry_count >= retry_max:
                self._banner_debug(
                    f"Retry planlanmadı. Limit dolu: {retry_count}/{retry_max}"
                )
                return

            self._banner_debug(
                f"Banner tekrar denemesi planlandı. {delay} sn sonra."
            )
            Clock.schedule_once(self._try_start_banner, float(delay))
        except Exception:
            self._banner_debug("_schedule_banner_retry başarısız.")
            self._banner_debug(traceback.format_exc())
            self._banner_popup_debug(
                traceback.format_exc(),
                title="Banner Retry Hatası",
            )