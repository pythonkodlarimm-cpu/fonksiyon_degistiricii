# -*- coding: utf-8 -*-
"""
DOSYA: app/core/tarama/tarayici.py

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
- Nested 9-10+ derinlikte kararlı ve deterministik çalışır
- Kod değiştirme akışı için stabil path / source / signature üretir

HIZ / KARARLILIK:
- ast.get_source_segment kullanılmaz
- Kaynak dilimleme hızlı offset + güvenli fallback hibrit yaklaşımıyla yapılır
- normalize / split / offset hazırlığı tek sefer yapılır
- Full parse hızlı ana yol olarak korunur
- Recovery yalnızca SyntaxError durumunda devreye girer
- Traversal yalnızca ilgili AST düğümlerine odaklanır

APK / ANDROID NOTLARI:
- Saf Python çalışır
- Dosya seçici Android'de sistem picker kullanabilir
- Seçilen dosya geçici klasöre kopyalanmış path olarak gelebilir
- Sabit proje kökü veya sabit depolama yolu varsayılmaz
- Android API 35 ile sorunsuz çalışacak şekilde platform bağımsızdır
- Hata mesajları kontrollü ve kullanıcı dostudur

SURUM: 10
TARIH: 2026-03-20
IMZA: FY.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import List

from app.core.modeller import FunctionItem


class FunctionScanError(ValueError):
    """Fonksiyon tarama sırasında oluşan kontrollü hata."""


# =========================================================
# NORMALIZE / IO
# =========================================================
def _normalize_text(text: str) -> str:
    s = str(text or "")
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    if not s.endswith("\n"):
        s += "\n"
    return s


def _normalize_path(file_path: str | Path) -> Path:
    raw = str(file_path or "").strip()
    if not raw:
        raise FunctionScanError("Dosya yolu boş.")
    return Path(raw)


def _read_text(file_path: str | Path) -> str:
    yol = _normalize_path(file_path)
    return yol.read_text(encoding="utf-8")


# =========================================================
# SOURCE HELPERS
# =========================================================
def _build_line_start_offsets(source_code: str) -> list[int]:
    """
    1-indexed satır mantığına uygun offset listesi üretir.

    Örnek:
    line_starts[0] -> 1. satır başlangıcı için 0
    line_starts[1] -> 2. satır başlangıç offset'i
    ...
    """
    starts = [0]
    idx = 0
    for line in source_code.splitlines(keepends=True):
        idx += len(line)
        starts.append(idx)
    return starts


def _safe_line_number(lineno: int, max_line: int) -> int:
    if lineno < 1:
        return 1
    if lineno > max_line:
        return max_line
    return lineno


def _node_signature(source_lines: list[str], node: ast.AST) -> str:
    """
    İmza için mümkünse fonksiyonun başladığı ilk satırı verir.
    Çok satırlı imzalarda yalnızca ilk satır döner.
    """
    try:
        lineno = int(getattr(node, "lineno", 0) or 0)
        if 0 < lineno <= len(source_lines):
            return str(source_lines[lineno - 1]).rstrip("\n")
    except Exception:
        pass
    return ""


def _extract_node_source_safe(
    source_code: str,
    source_lines: list[str],
    line_starts: list[int],
    node: ast.AST,
) -> str:
    """
    Hibrit yaklaşım:
    1) Hızlı offset tabanlı slicing
    2) Şüpheli sonuçta güvenli line fallback

    Amaç:
    - hızdan ödün vermeden stabil kaynak üretmek
    - nested / method / async yapıda güvenilir kalmak
    """
    total_lines = max(1, len(source_lines))

    lineno = int(getattr(node, "lineno", 1) or 1)
    end_lineno = int(getattr(node, "end_lineno", lineno) or lineno)
    col_offset = int(getattr(node, "col_offset", 0) or 0)
    end_col_offset = int(getattr(node, "end_col_offset", 0) or 0)

    lineno = _safe_line_number(lineno, total_lines)
    end_lineno = _safe_line_number(end_lineno, total_lines)

    # -----------------------------------------------------
    # FAST PATH
    # -----------------------------------------------------
    try:
        start_idx = line_starts[lineno - 1] + max(0, col_offset)

        if end_lineno <= total_lines:
            if end_col_offset > 0:
                end_idx = line_starts[end_lineno - 1] + end_col_offset
            else:
                end_idx = line_starts[end_lineno]
        else:
            end_idx = len(source_code)

        if end_idx > start_idx:
            result = source_code[start_idx:end_idx].rstrip("\n")

            # Sağlamlık kontrolü:
            # Hedefimiz fonksiyonun / class'ın gerçek başlangıcını kaçırmamak.
            stripped = result.lstrip()
            if stripped.startswith(("def ", "async def ", "class ", "@")):
                return result
    except Exception:
        pass

    # -----------------------------------------------------
    # SAFE FALLBACK
    # -----------------------------------------------------
    try:
        return "".join(source_lines[lineno - 1:end_lineno]).rstrip("\n")
    except Exception:
        return ""


# =========================================================
# FAIL-SOFT RECOVERY HELPERS
# =========================================================
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
    lines = source_code.splitlines(keepends=True)

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
        mod = ast.parse(block_text)
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


# =========================================================
# COLLECTOR
# =========================================================
class _FunctionCollector(ast.NodeVisitor):
    def __init__(self, source_code: str, file_path: str = ""):
        self.source_code = source_code
        self.source_lines = self.source_code.splitlines(keepends=True)
        self.line_starts = _build_line_start_offsets(self.source_code)
        self.file_path = str(file_path or "")
        self.items: List[FunctionItem] = []

        self.scope_stack: list[str] = []
        self.class_stack: list[str] = []
        self._seen_keys: set[tuple[str, int, int]] = set()

    def visit(self, node):
        """
        Traversal maliyetini azaltmak için yalnızca gerekli çocukları ziyaret eder.
        """
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            return super().visit(node)

        for child in ast.iter_child_nodes(node):
            self.visit(child)

    def _current_parent_name(self) -> str:
        if not self.scope_stack:
            return ""
        return self.scope_stack[-1]

    def _qualified_name_for(self, current_name: str) -> str:
        parts = self.scope_stack + [current_name]
        return ".".join([p for p in parts if p])

    def _indent_level(self) -> int:
        return min(len(self.scope_stack), 64)

    def _is_nested(self) -> bool:
        return len(self.scope_stack) > 0

    def _is_inside_class(self) -> bool:
        return len(self.class_stack) > 0

    def _kind_for_function(self, node: ast.AST) -> str:
        is_async = isinstance(node, ast.AsyncFunctionDef)
        is_nested = self._is_nested()
        inside_class = self._is_inside_class()

        if inside_class and is_nested:
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
        source = _extract_node_source_safe(
            self.source_code,
            self.source_lines,
            self.line_starts,
            node,
        )

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


# =========================================================
# SCAN CORE
# =========================================================
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


# =========================================================
# PUBLIC API
# =========================================================
def scan_functions_from_code(
    source_code: str,
    file_path: str = "<memory>",
) -> List[FunctionItem]:
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
    """
    Dosya yolundan Python fonksiyonlarını tarar.

    Not:
    - Android'de bu yol, sistem picker sonrası geçici klasöre kopyalanmış dosya olabilir
    - Sabit kök dizin varsayılmaz
    - Uzantı kontrolü zorunlu tutulmaz; içerik parse edilebiliyorsa taranır
    """
    path_obj = _normalize_path(file_path)

    try:
        if not path_obj.exists():
            raise FunctionScanError(f"Dosya bulunamadı: {path_obj}")

        if not path_obj.is_file():
            raise FunctionScanError(f"Geçerli bir dosya değil: {path_obj}")
    except OSError as exc:
        raise FunctionScanError(f"Dosya erişim hatası: {path_obj}") from exc

    try:
        source_code = _read_text(path_obj)
    except UnicodeDecodeError as exc:
        raise FunctionScanError(f"Dosya utf-8 ile okunamadı: {path_obj}") from exc
    except OSError as exc:
        raise FunctionScanError(f"Dosya okunamadı: {path_obj}") from exc

    try:
        normalized_path = str(path_obj.resolve())
    except Exception:
        normalized_path = str(path_obj)

    return scan_functions_from_code(source_code, file_path=normalized_path)