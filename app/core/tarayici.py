# -*- coding: utf-8 -*-
"""
DOSYA: app/core/tarayici.py

ROL:
- Python kaynak kodu içindeki function / async function tanımlarını tarar
- Nested function ve class method yapısını destekler
- FunctionItem listesi üretir
- Hatalı parse durumlarını kontrollü biçimde bildirir

GÜÇLENDİRME:
- Normal AST parse başarısız olursa fail-soft kurtarma dener
- Bozuk dosyada parse edilebilen blokları yine de toplamaya çalışır
- Function / async function / class bloklarını satır tabanlı ayıklar
- Tam çökme yerine mümkün olduğunca sonuç üretir

APK / ANDROID NOTLARI:
- Saf Python çalışır
- Path tabanlı dosya erişimi kullanılır
- Hata mesajları kontrollü ve kullanıcı dostudur

SURUM: 5
TARIH: 2026-03-14
IMZA: FY.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import List

from app.core.modeller import FunctionItem


class FunctionScanError(ValueError):
    """Fonksiyon tarama sırasında oluşan kontrollü hata."""


def _normalize_text(text: str) -> str:
    s = str(text or "")
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    if not s.endswith("\n"):
        s += "\n"
    return s


def _read_text(file_path: str | Path) -> str:
    yol = Path(file_path)
    return yol.read_text(encoding="utf-8")


def _safe_get_source_segment(source_text: str, node: ast.AST) -> str:
    try:
        seg = ast.get_source_segment(source_text, node)
        if isinstance(seg, str) and seg.strip():
            return _normalize_text(seg).rstrip("\n")
    except Exception:
        pass

    try:
        lines = source_text.splitlines()
        start = max(1, int(getattr(node, "lineno", 1) or 1))
        end = max(start, int(getattr(node, "end_lineno", start) or start))
        return "\n".join(lines[start - 1:end]).rstrip("\n")
    except Exception:
        return ""


def _leading_spaces(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _is_block_start(stripped_line: str) -> bool:
    s = stripped_line.strip()
    return s.startswith("def ") or s.startswith("async def ") or s.startswith("class ")


def _collect_candidate_blocks(source_code: str) -> list[tuple[int, int, str]]:
    """
    SyntaxError durumunda kaba kurtarma için:
    - def / async def / class ile başlayan blokları toplar
    - aynı veya daha düşük indentte yeni blok görünene kadar genişletir
    """
    normalized = _normalize_text(source_code)
    lines = normalized.splitlines(keepends=True)

    blocks: list[tuple[int, int, str]] = []
    i = 0
    total = len(lines)

    while i < total:
        line = lines[i]
        stripped = line.lstrip(" ")

        if not _is_block_start(stripped):
            i += 1
            continue

        start = i
        base_indent = _leading_spaces(line)
        j = i + 1

        while j < total:
            next_line = lines[j]
            next_stripped_full = next_line.strip()

            if not next_stripped_full:
                j += 1
                continue

            next_indent = _leading_spaces(next_line)
            next_lstripped = next_line.lstrip(" ")

            if _is_block_start(next_lstripped) and next_indent <= base_indent:
                break

            j += 1

        block_text = "".join(lines[start:j])
        blocks.append((start + 1, j, block_text))
        i = j

    return blocks


def _parse_candidate_block(block_text: str):
    try:
        mod = ast.parse(_normalize_text(block_text))
    except Exception:
        return None

    if not mod.body:
        return None

    return mod


def _shift_node_positions(node: ast.AST, line_offset: int) -> None:
    """
    Kurtarma parse'ında blok başından üretilen AST satırlarını
    gerçek dosya satırlarına taşır.
    """
    for child in ast.walk(node):
        if hasattr(child, "lineno") and getattr(child, "lineno", None) is not None:
            child.lineno = int(child.lineno) + line_offset
        if hasattr(child, "end_lineno") and getattr(child, "end_lineno", None) is not None:
            child.end_lineno = int(child.end_lineno) + line_offset


def _node_signature(source_lines: list[str], node: ast.AST) -> str:
    """
    İmza için mümkünse fonksiyonun başladığı satırı verir.
    Çok satırlı imzalarda ilk satır döner.
    """
    try:
        lineno = int(getattr(node, "lineno", 0) or 0)
        if 0 < lineno <= len(source_lines):
            return str(source_lines[lineno - 1]).rstrip("\n")
    except Exception:
        pass
    return ""


def _extract_node_source(source_code: str, source_lines: list[str], node: ast.AST) -> str:
    seg = _safe_get_source_segment(source_code, node)
    if seg.strip():
        return seg

    lineno = int(getattr(node, "lineno", 1) or 1)
    end_lineno = int(getattr(node, "end_lineno", lineno) or lineno)

    try:
        chunk = "".join(source_lines[lineno - 1:end_lineno])
        return _normalize_text(chunk).rstrip("\n")
    except Exception:
        return ""


class _FunctionCollector(ast.NodeVisitor):
    def __init__(self, source_code: str, file_path: str = ""):
        self.source_code = _normalize_text(source_code)
        self.source_lines = self.source_code.splitlines(keepends=True)
        self.file_path = str(file_path or "")
        self.items: List[FunctionItem] = []

        self.scope_stack: list[str] = []
        self.class_stack: list[str] = []
        self._seen_keys: set[tuple[str, int, int, str]] = set()

    # ---------------------------------------------------------
    # yardımcılar
    # ---------------------------------------------------------
    def _current_parent_name(self) -> str:
        if not self.scope_stack:
            return ""
        return self.scope_stack[-1]

    def _qualified_name_for(self, current_name: str) -> str:
        parts = self.scope_stack + [current_name]
        return ".".join([p for p in parts if p])

    def _indent_level(self) -> int:
        return len(self.scope_stack)

    def _is_nested(self) -> bool:
        return len(self.scope_stack) > 0

    def _is_inside_class(self) -> bool:
        return len(self.class_stack) > 0

    def _kind_for_function(self, node: ast.AST) -> str:
        is_async = isinstance(node, ast.AsyncFunctionDef)
        is_nested = self._is_nested()
        inside_class = self._is_inside_class()

        if inside_class and is_nested:
            # class içi method veya method içi nested olabilir
            # scope_stack örnekleri:
            #   ["Kisi"] -> tam_ad
            #   ["Kisi", "etiket"] -> _yas_metni
            if len(self.class_stack) == 1 and len(self.scope_stack) == 1:
                return "async_method" if is_async else "method"
            return "async_nested" if is_async else "nested"

        if inside_class:
            return "async_method" if is_async else "method"

        if is_nested:
            return "async_nested" if is_async else "nested"

        return "async_function" if is_async else "function"

    def _append_item(self, item: FunctionItem) -> None:
        key = (
            str(getattr(item, "path", "") or ""),
            int(getattr(item, "lineno", 0) or 0),
            int(getattr(item, "end_lineno", 0) or 0),
            str(getattr(item, "kind", "") or ""),
        )

        if key in self._seen_keys:
            return

        self._seen_keys.add(key)
        self.items.append(item)

    def _make_item(self, node: ast.AST) -> None:
        name = str(getattr(node, "name", "") or "").strip()
        if not name:
            return

        lineno = int(getattr(node, "lineno", 1) or 1)
        end_lineno = int(getattr(node, "end_lineno", lineno) or lineno)
        col_offset = int(getattr(node, "col_offset", 0) or 0)
        end_col_offset = int(getattr(node, "end_col_offset", 0) or 0)

        qualified_name = self._qualified_name_for(name)
        parent_name = self._current_parent_name()
        indent_level = self._indent_level()
        is_nested = self._is_nested()
        kind = self._kind_for_function(node)
        signature = _node_signature(self.source_lines, node)
        source = _extract_node_source(self.source_code, self.source_lines, node)

        item = FunctionItem(
            path=qualified_name if qualified_name else name,
            name=name,
            kind=kind,
            lineno=lineno,
            end_lineno=end_lineno,
            col_offset=col_offset,
            end_col_offset=end_col_offset,
            signature=signature,
            source=source,
        )

        try:
            item.qualified_name = qualified_name
        except Exception:
            pass

        try:
            item.parent_name = parent_name
        except Exception:
            pass

        try:
            item.indent_level = indent_level
        except Exception:
            pass

        try:
            item.is_nested = is_nested
        except Exception:
            pass

        try:
            item.file_path = self.file_path
        except Exception:
            pass

        self._append_item(item)

    # ---------------------------------------------------------
    # ziyaret
    # ---------------------------------------------------------
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        class_name = str(getattr(node, "name", "") or "").strip()

        if not class_name:
            self.generic_visit(node)
            return

        self.scope_stack.append(class_name)
        self.class_stack.append(class_name)

        try:
            self.generic_visit(node)
        finally:
            if self.class_stack:
                self.class_stack.pop()
            if self.scope_stack:
                self.scope_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._make_item(node)
        self.scope_stack.append(str(getattr(node, "name", "") or ""))

        try:
            self.generic_visit(node)
        finally:
            if self.scope_stack:
                self.scope_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._make_item(node)
        self.scope_stack.append(str(getattr(node, "name", "") or ""))

        try:
            self.generic_visit(node)
        finally:
            if self.scope_stack:
                self.scope_stack.pop()


def _sort_items(items: List[FunctionItem]) -> List[FunctionItem]:
    return sorted(
        items,
        key=lambda x: (
            int(getattr(x, "lineno", 0) or 0),
            str(getattr(x, "path", "") or "").lower(),
        ),
    )


def _scan_with_full_parse(normalized: str, file_path: str = "") -> List[FunctionItem]:
    tree = ast.parse(normalized)
    collector = _FunctionCollector(normalized, file_path=file_path)
    collector.visit(tree)
    return _sort_items(collector.items)


def _scan_with_fail_soft_recovery(normalized: str, file_path: str = "") -> List[FunctionItem]:
    """
    Tam parse bozulduğunda:
    - aday blokları bul
    - parse edilebilenleri ziyaret et
    - elde edilen fonksiyonları topla
    """
    collector = _FunctionCollector(normalized, file_path=file_path)
    blocks = _collect_candidate_blocks(normalized)

    for start_lineno, _end_lineno, block_text in blocks:
        mod = _parse_candidate_block(block_text)
        if mod is None:
            continue

        line_offset = start_lineno - 1

        for node in mod.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue

            _shift_node_positions(node, line_offset)
            collector.visit(node)

    return _sort_items(collector.items)


def scan_functions_from_code(source_code: str, file_path: str = "<memory>") -> List[FunctionItem]:
    normalized = _normalize_text(source_code)

    if not normalized.strip():
        return []

    try:
        return _scan_with_full_parse(normalized, file_path=file_path)
    except SyntaxError as full_exc:
        recovered = _scan_with_fail_soft_recovery(normalized, file_path=file_path)
        if recovered:
            return recovered

        raise FunctionScanError(
            f"Kaynak kod parse edilemedi: satır {full_exc.lineno}, sütun {full_exc.offset} -> {full_exc.msg}"
        ) from full_exc


def scan_functions_from_file(file_path: str | Path) -> List[FunctionItem]:
    raw_path = str(file_path or "").strip()
    if not raw_path:
        raise FunctionScanError("Dosya yolu boş.")

    path_obj = Path(raw_path)

    if not path_obj.exists():
        raise FunctionScanError(f"Dosya bulunamadı: {path_obj}")

    if not path_obj.is_file():
        raise FunctionScanError(f"Geçerli bir dosya değil: {path_obj}")

    try:
        source_code = _read_text(path_obj)
    except UnicodeDecodeError as exc:
        raise FunctionScanError(f"Dosya utf-8 ile okunamadı: {path_obj}") from exc
    except OSError as exc:
        raise FunctionScanError(f"Dosya okunamadı: {path_obj}") from exc

    return scan_functions_from_code(source_code, file_path=str(path_obj.resolve()))