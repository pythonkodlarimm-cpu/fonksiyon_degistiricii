# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dosya_secici_paketi/pickers/android_dokuman.py

ROL:
- Android gerçek sistem dosya seçicisini açar
- Seçilen dosyayı URI olarak alır
- Yalnızca sade DocumentSelection üretir

NOT:
- Bu dosya sadece seçim yapar
- İçe aktarma, tarama, yedekleme burada yapılmaz

API UYUMLULUK:
- SAF (Storage Access Framework) tabanlı ACTION_OPEN_DOCUMENT kullanılır
- Persistable URI izni alınmaya çalışılır
- Activity ve intent kontrolleri güçlendirilmiştir
- Tekli dosya seçimi için güvenli akış korunmuştur
- API 35 uyumludur

SURUM: 3
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from kivy.utils import platform

from app.services.android import AndroidYoneticisi
from app.ui.dosya_secici_paketi.models import DocumentSelection


class AndroidDokumanSecici:
    ANDROID_REQUEST_CODE = 10240

    def __init__(self, owner, on_selected):
        self.owner = owner
        self.on_selected = on_selected
        self._is_bound = False
        self._android = AndroidYoneticisi()
        self._bind_activity_result()

    def _debug(self, message: str) -> None:
        try:
            self.owner._debug(f"[ANDROID_DOKUMAN_SECICI] {message}")
        except Exception:
            try:
                print("[ANDROID_DOKUMAN_SECICI]", str(message))
            except Exception:
                pass

    def _bind_activity_result(self) -> None:
        """
        Android activity result callback bind eder.
        """
        if platform != "android":
            return

        if self._is_bound:
            return

        try:
            from android import activity  # type: ignore

            activity.bind(on_activity_result=self._on_activity_result)
            self._is_bound = True
            self._debug("activity result bind edildi")
        except Exception as exc:
            self._debug(f"bind hatası: {exc}")

    def secici_ac(self) -> None:
        """
        Android sistem dosya seçicisini açar.
        """
        if platform != "android":
            self._debug("Android değil")
            return

        try:
            from jnius import autoclass, cast  # type: ignore

            Intent = autoclass("android.content.Intent")
            PythonActivity = autoclass("org.kivy.android.PythonActivity")

            current_activity = cast("android.app.Activity", PythonActivity.mActivity)
            if current_activity is None:
                self._debug("seçici açılamadı: activity boş")
                return

            intent = Intent(Intent.ACTION_OPEN_DOCUMENT)
            intent.addCategory(Intent.CATEGORY_OPENABLE)
            intent.setType("*/*")

            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            intent.addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
            intent.addFlags(Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION)

            current_activity.startActivityForResult(intent, self.ANDROID_REQUEST_CODE)
            self._debug("seçici açıldı")

        except Exception as exc:
            self._debug(f"seçici açma hatası: {exc}")

    def _on_activity_result(self, request_code, result_code, intent) -> None:
        """
        Dosya seçici dönüşünü yakalar ve DocumentSelection üretir.
        """
        if request_code != self.ANDROID_REQUEST_CODE:
            return

        try:
            from jnius import autoclass

            Activity = autoclass("android.app.Activity")

            if result_code != Activity.RESULT_OK:
                self._debug("seçim iptal edildi")
                return

            if intent is None:
                self._debug("intent boş")
                return

            uri = intent.getData()
            if uri is None:
                self._debug("uri boş")
                return

            uri_str = str(uri.toString() or "").strip()
            if not uri_str:
                self._debug("uri string boş")
                return

            if not self._android.is_android_document_uri(uri_str):
                self._debug("geçersiz android document uri")
                return

            display_name = ""
            mime_type = ""

            try:
                self._android.take_persistable_permission(intent, uri_str)
                self._debug("persistable izin alındı")
            except Exception as exc:
                self._debug(f"persistable izin alınamadı: {exc}")

            try:
                display_name = str(self._android.get_display_name(uri_str) or "").strip()
            except Exception as exc:
                self._debug(f"display name alınamadı: {exc}")

            try:
                mime_type = str(self._android.get_mime_type(uri_str) or "").strip()
            except Exception as exc:
                self._debug(f"mime type alınamadı: {exc}")

            secim = DocumentSelection(
                source="android_document",
                uri=uri_str,
                local_path="",
                display_name=display_name,
                mime_type=mime_type,
            )

            self._debug(
                f"seçim tamam | uri={uri_str} | display={display_name} | mime={mime_type}"
            )

            if self.on_selected:
                self.on_selected(secim)

        except Exception as exc:
            self._debug(f"activity result hatası: {exc}")