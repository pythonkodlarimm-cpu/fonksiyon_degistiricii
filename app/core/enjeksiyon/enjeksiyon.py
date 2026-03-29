# -*- coding: utf-8 -*-
"""
DOSYA: app/core/enjeksiyon/enjeksiyon.py

ROL:
- Fonksiyon içine AST tabanlı kod enjeksiyonu sağlar
- Hedef fonksiyon içinde belirli noktalara güvenli şekilde kod ekler
- Dosya bazlı çalışma + motor bazlı yedekleme entegrasyonu içerir

DESTEKLENEN MODLAR:
- if → ilk if bloğunun başına ekler
- try → ilk try bloğunun başına ekler
- before_return → tüm return ifadelerinden hemen önce ekler

MİMARİ:
- AST parse → hedef bul → node mutate → unparse
- String replace yok
- Deterministik eşleşme (path + lineno + kind)
- Lazy import + type-safe cache
- Yedekleme motoru ile entegre (motor adı: "enjeksiyon")

API UYUMLULUK:
- Platform bağımsız
- Android API 35 uyumlu
- Pydroid3 / masaüstü aynı davranış

SURUM: 5
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

import ast
import os
import textwrap
from pathlib import Path
from typing import Callable, Final, Type

from app.core.modeller.modeller import FunctionItem


# =========================================================
# SABİTLER
# =========================================================
INJECT_MODE_IF: Final[str] = "if"
INJECT_MODE_TRY: Final[str] = "try"
INJECT_MODE_BEFORE_RETURN: Final[str] = "before_return"

_ALLOWED_INJECT_MODES: Final[frozenset[str]] = frozenset(
    {
        INJECT_MODE_IF,
        INJECT_MODE_TRY,
        INJECT_MODE_BEFORE_RETURN,
    }
)


# =========================================================
# ERROR
# =========================================================
class FunctionInjectError(ValueError):
    pass


# =========================================================
# LAZY CACHE (TYPE SAFE)
# =========================================================
_backup_path_fn: Callable[..., Path] | None = None


def _backup_path():
    global _backup_path_fn
    if _backup_path_fn is None:
        from app.core.yedekleme.yollar import backup_dosya_yolu_uret

        _backup_path_fn = backup_dosya_yolu_uret
    return _backup_path_fn


# =========================================================
# PARSE
# =========================================================
def _parse_source(source_code: str) -> ast.Module:
    try:
        return ast.parse(str(source_code or ""))
    except SyntaxError as exc:
        raise FunctionInjectError("Kaynak parse edilemedi") from exc


def _normalize_inject_code(inject_code: str) -> str:
    code = textwrap.dedent(str(inject_code or "")).strip()
    if not code:
        raise FunctionInjectError("Inject kod boş")
    return code


def _parse_inject_statements(inject_code: str) -> list[ast.stmt]:
    normalized = _normalize_inject_code(inject_code)

    try:
        tree = ast.parse(normalized)
    except SyntaxError as exc:
        raise FunctionInjectError("Inject parse hatası") from exc

    return tree.body


def _validate_mode(mode: str) -> str:
    m = str(mode or "").strip().lower()
    if m not in _ALLOWED_INJECT_MODES:
        raise FunctionInjectError(f"Geçersiz mode: {mode}")
    return m


# =========================================================
# FIND (STRICT - TEK GEÇİŞ)
# =========================================================
def _find_target_function(
    tree: ast.Module,
    target: FunctionItem,
) -> ast.FunctionDef | ast.AsyncFunctionDef:
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if (
                node.name == target.name
                and int(node.lineno) == target.lineno
            ):
                return node

    raise FunctionInjectError("Fonksiyon bulunamadı")


# =========================================================
# INJECT
# =========================================================
class _ReturnInjector(ast.NodeTransformer):
    __slots__ = ("_inject",)

    def __init__(self, inject_statements: list[ast.stmt]) -> None:
        self._inject = inject_statements

    def visit_Return(self, node: ast.Return):
        return [*self._inject, node]


def _inject_if(fn: ast.AST, inject: list[ast.stmt]) -> None:
    for n in ast.walk(fn):
        if isinstance(n, ast.If):
            n.body = [*inject, *n.body]
            return
    raise FunctionInjectError("if bulunamadı")


def _inject_try(fn: ast.AST, inject: list[ast.stmt]) -> None:
    for n in ast.walk(fn):
        if isinstance(n, ast.Try):
            n.body = [*inject, *n.body]
            return
    raise FunctionInjectError("try bulunamadı")


def _inject_return(fn: ast.AST, inject: list[ast.stmt]) -> None:
    wrapper = ast.Module(body=fn.body, type_ignores=[])
    t = _ReturnInjector(inject)
    new_mod = t.visit(wrapper)
    ast.fix_missing_locations(new_mod)
    fn.body = new_mod.body


# =========================================================
# CORE
# =========================================================
def inject_code(
    source_code: str,
    target: FunctionItem,
    inject_code: str,
    *,
    mode: str,
) -> str:
    tree = _parse_source(source_code)
    fn = _find_target_function(tree, target)

    inject_nodes = _parse_inject_statements(inject_code)
    mode = _validate_mode(mode)

    if mode == INJECT_MODE_IF:
        _inject_if(fn, inject_nodes)
    elif mode == INJECT_MODE_TRY:
        _inject_try(fn, inject_nodes)
    else:
        _inject_return(fn, inject_nodes)

    ast.fix_missing_locations(tree)

    try:
        result = ast.unparse(tree)
    except Exception as exc:
        raise FunctionInjectError("Unparse hatası") from exc

    try:
        ast.parse(result)
    except SyntaxError as exc:
        raise FunctionInjectError("Final syntax bozuk") from exc

    return result


# =========================================================
# FILE (YEDEK ENTEGRE)
# =========================================================
def inject_code_in_file(
    file_path: str,
    target: FunctionItem,
    inject_code_str: str,
    *,
    mode: str,
    backup: bool = True,
    encoding: str = "utf-8",
) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FunctionInjectError("Dosya yok")

    source = path.read_text(encoding=encoding)

    updated = inject_code(
        source_code=source,
        target=target,
        inject_code=inject_code_str,
        mode=mode,
    )

    # =========================================================
    # BACKUP (MOTOR BAZLI)
    # =========================================================
    if backup:
        backup_path = _backup_path()(
            motor_adi="enjeksiyon",
            kaynak_dosya_adi=path.name,
        )
        backup_path.write_text(source, encoding=encoding)

    # =========================================================
    # ATOMIC WRITE
    # =========================================================
    tmp = path.with_suffix(".tmp")
    tmp.write_text(updated, encoding=encoding)
    os.replace(tmp, path)

    return updated