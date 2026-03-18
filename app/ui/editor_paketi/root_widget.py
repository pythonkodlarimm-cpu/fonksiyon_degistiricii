# -*- coding: utf-8 -*-
from __future__ import annotations

from app.ui.editor_paketi.editor_paneli import EditorPaneli


class RootWidget(EditorPaneli):
    """
    RootWidget bekleyen yerler için doğrudan kullanılabilir uyum sınıfı.
    """

    def __init__(self, on_update=None, on_restore=None, **kwargs):
        super().__init__(
            on_update=on_update or self._dummy_update,
            on_restore=on_restore or self._dummy_restore,
            **kwargs,
        )

    def _dummy_update(self, item, yeni_kod):
        self._set_status_error("on_update callback bağlı değil.", 0)
        self.inline_notice.show(
            title="Bağlantı hatası",
            text="on_update callback bağlı değil.",
            icon_name="error.png",
            tone="error",
            duration=4.0,
        )

    def _dummy_restore(self):
        self._set_status_error("on_restore callback bağlı değil.", 0)
        self.inline_notice.show(
            title="Bağlantı hatası",
            text="on_restore callback bağlı değil.",
            icon_name="error.png",
            tone="error",
            duration=4.0,
        )