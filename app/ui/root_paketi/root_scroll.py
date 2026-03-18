# -*- coding: utf-8 -*-
from __future__ import annotations

from kivy.clock import Clock
from kivy.metrics import dp


class RootScrollMixin:
    def _safe_scroll_to_widget(self, widget, extra_top_padding: float = 0.0) -> None:
        try:
            if self.scroll is None or self.main_column is None or widget is None:
                return

            viewport_h = float(getattr(self.scroll, "height", 0) or 0)
            content_h = float(getattr(self.main_column, "height", 0) or 0)
            widget_y = float(getattr(widget, "y", 0) or 0)

            if content_h <= 0 or viewport_h <= 0:
                return

            max_scroll_distance = max(1.0, content_h - viewport_h)
            hedef = (widget_y + float(extra_top_padding or 0.0)) / max_scroll_distance
            hedef = max(0.0, min(1.0, hedef))

            self.scroll.scroll_y = hedef
            Clock.schedule_once(lambda *_: setattr(self.scroll, "scroll_y", hedef), 0)
            Clock.schedule_once(lambda *_: setattr(self.scroll, "scroll_y", hedef), 0.05)
        except Exception as exc:
            self._debug(f"scroll to widget hatası: {exc}")

    def _scroll_to_function_list(self) -> None:
        try:
            if self.function_list is None:
                return

            def _go(*_args):
                self._safe_scroll_to_widget(self.function_list, extra_top_padding=dp(120))

            Clock.schedule_once(_go, 0)
            Clock.schedule_once(_go, 0.08)
        except Exception as exc:
            self._debug(f"function list scroll hatası: {exc}")

    def _scroll_to_editor(self) -> None:
        try:
            if self.editor is None:
                return

            def _go(*_args):
                self._safe_scroll_to_widget(self.editor, extra_top_padding=dp(160))

            Clock.schedule_once(_go, 0)
            Clock.schedule_once(_go, 0.08)
        except Exception as exc:
            self._debug(f"editor scroll hatası: {exc}")

    def _focus_new_code_area(self) -> None:
        try:
            if self.editor is None or getattr(self.editor, "new_code_area", None) is None:
                return

            def _focus(*_args):
                try:
                    editor_widget = getattr(self.editor.new_code_area, "editor", None)
                    if editor_widget is None:
                        return

                    editor_widget.focus = True
                    editor_widget.cursor = (0, 0)
                    editor_widget.scroll_to_top()
                except Exception:
                    pass

            Clock.schedule_once(_focus, 0.12)
            Clock.schedule_once(_focus, 0.22)
        except Exception as exc:
            self._debug(f"new code focus hatası: {exc}")