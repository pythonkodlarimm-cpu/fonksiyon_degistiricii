# -*- coding: utf-8 -*-
from __future__ import annotations


class RootStatusMixin:
    def _safe_set_status(self, text: str, icon_name: str = "") -> None:
        try:
            if self.status is not None:
                self.status.set_status(text, icon_name=icon_name)
        except Exception:
            pass

    def set_status(self, text: str, icon_name: str = "") -> None:
        self._safe_set_status(text, icon_name)

    def set_status_info(self, text: str, icon_name: str = "") -> None:
        try:
            if self.status is not None:
                self.status.set_status(text, icon_name=icon_name)
        except Exception:
            pass

    def set_status_success(self, text: str) -> None:
        try:
            if self.status is not None:
                self.status.set_success(text)
        except Exception:
            pass

    def set_status_warning(self, text: str) -> None:
        try:
            if self.status is not None:
                self.status.set_warning(text)
        except Exception:
            pass

    def set_status_error(self, text: str) -> None:
        try:
            if self.status is not None:
                self.status.set_error(text)
        except Exception:
            pass

    def show_toast(self, text: str, icon_name: str = "", duration: float = 2.4) -> None:
        if self.toast_layer is None:
            return

        try:
            self._get_gecici_bildirim_servisi().show(
                text=str(text or ""),
                icon_name=str(icon_name or ""),
                duration=float(duration or 2.4),
            )
        except Exception:
            pass

    def hide_toast(self) -> None:
        if self.toast_layer is None:
            return

        try:
            self._get_gecici_bildirim_servisi().hide_immediately()
        except Exception:
            pass

    def _on_file_access_status_changed(self, durum: bool) -> None:
        try:
            if durum:
                self.set_status_success("Tüm dosya erişimi açık.")
            else:
                self.set_status_warning("Tüm dosya erişimi kapalı.")
        except Exception:
            pass