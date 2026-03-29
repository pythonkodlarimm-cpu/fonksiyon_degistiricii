# -*- coding: utf-8 -*-
"""
DOSYA: app/core/tarama/tarayici.py

ROL:
- Python kaynak kodundan function / async function / method / nested function tarar
- Deterministik, stabil ve replace-safe FunctionItem listesi üretir
- Yeni fonksiyon kodu için top-level doğrulama yardımcılarını sağlar

GÜÇLENDİRME:
- Full AST parse + blok bazlı fail-soft recovery
- Decorator aware (üst decorator’ları dahil eder)
- Büyük dosyalarda (10k+ satır) performans stabil
- Path üretimi deterministik (replace için kritik)
- AST traversal minimal (gereksiz node yok)
- Tek top-level fonksiyon doğrulaması core katmanına taşındı
- Nested fonksiyonlar serbest, top-level fonksiyon sayısı kesin kontrol edilir

TYPE GÜVENLİĞİ:
- Çıkış tipi: list[FunctionItem]
- Internal state izole
- Runtime attribute injection yok
- Doğrulama çıktısı deterministik dict yapısıdır

ANDROID UYUMLULUK:
- UTF-8 safe
- Path bağımsız
- Crash yerine kontrollü hata

SURUM: 13
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any, List

from app.core.modeller import FunctionItem


# =========================================================
# ERROR
# =========================================================
class FunctionScanError(ValueError):
    """
    Fonksiyon tarama ve doğrulama hatası.
    """


# =========================================================
# NORMALIZE
# =========================================================
def _normalize_text(text: str) -> str:
    s = str(text or "")
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    return s if s.endswith("\n") else s + "\n"


def _normalize_path(file_path: str | Path) -> Path:
    raw = str(file_path or "").strip()
    if not raw:
        raise FunctionScanError("Dosya yolu boş.")
    return Path(raw)


# =========================================================
# SOURCE CONTEXT
# =========================================================
class _Ctx:
    __slots__ = ("src", "lines", "starts")

    def __init__(self, src: str):
        self.src = src
        self.lines = src.splitlines(keepends=True)
        self.starts = self._offsets()

    def _offsets(self) -> list[int]:
        out = [0]
        idx = 0
        for l in self.lines:
            idx += len(l)
            out.append(idx)
        return out


# =========================================================
# SAFE
# =========================================================
def _i(v, d=0):
    try:
        return int(v)
    except Exception:
        return d


def _line(n, max_):
    return 1 if n < 1 else max_ if n > max_ else n


# =========================================================
# SOURCE EXTRACTION (DECORATOR AWARE)
# =========================================================
def _extract(ctx: _Ctx, node: ast.AST) -> str:
    total = len(ctx.lines) or 1

    lineno = _line(_i(getattr(node, "lineno", 1)), total)
    end_lineno = _line(_i(getattr(node, "end_lineno", lineno)), total)

    col = _i(getattr(node, "col_offset", 0))
    end_col = _i(getattr(node, "end_col_offset", 0))

    deco = getattr(node, "decorator_list", None)
    if deco:
        try:
            lineno = min(d.lineno for d in deco if hasattr(d, "lineno"))
        except Exception:
            pass

    try:
        start = ctx.starts[lineno - 1] + max(0, col)

        if end_col > 0:
            end = ctx.starts[end_lineno - 1] + end_col
        else:
            end = ctx.starts[end_lineno]

        if end > start:
            out = ctx.src[start:end].rstrip("\n")
            if out.lstrip().startswith(("def ", "async def ", "@", "class ")):
                return out
    except Exception:
        pass

    return "".join(ctx.lines[lineno - 1:end_lineno]).rstrip("\n")


def _sig(ctx: _Ctx, node: ast.AST) -> str:
    ln = _i(getattr(node, "lineno", 0))
    if 1 <= ln <= len(ctx.lines):
        return ctx.lines[ln - 1].rstrip("\n")
    return ""


# =========================================================
# COLLECTOR
# =========================================================
class _Collector(ast.NodeVisitor):
    __slots__ = ("ctx", "file", "items", "scope", "class_scope", "seen")

    def __init__(self, ctx: _Ctx, file_path: str):
        self.ctx = ctx
        self.file = file_path
        self.items: List[FunctionItem] = []
        self.scope: list[str] = []
        self.class_scope: list[str] = []
        self.seen: set[tuple[str, int, int]] = set()

    def _kind(self, n):
        a = isinstance(n, ast.AsyncFunctionDef)
        c = bool(self.class_scope)
        s = bool(self.scope)

        if c and s:
            return "async_nested" if a else "nested"
        if c:
            return "async_method" if a else "method"
        if s:
            return "async_nested" if a else "nested"
        return "async_function" if a else "function"

    def _add(self, it: FunctionItem):
        k = (it.path, it.lineno, it.end_lineno)
        if k in self.seen:
            return
        self.seen.add(k)
        self.items.append(it)

    def _make(self, n):
        name = getattr(n, "name", "").strip()
        if not name:
            return

        ln = _i(getattr(n, "lineno", 1))
        eln = _i(getattr(n, "end_lineno", ln))

        path = ".".join(self.scope + [name]) if self.scope else name

        it = FunctionItem(
            path=path,
            name=name,
            kind=self._kind(n),
            lineno=ln,
            end_lineno=eln,
            col_offset=_i(getattr(n, "col_offset", 0)),
            end_col_offset=_i(getattr(n, "end_col_offset", 0)),
            signature=_sig(self.ctx, n),
            source=_extract(self.ctx, n),
        )

        if hasattr(it, "file_path"):
            it.file_path = self.file

        self._add(it)

    def visit_ClassDef(self, n):
        self.scope.append(n.name)
        self.class_scope.append(n.name)
        try:
            self.generic_visit(n)
        finally:
            self.scope.pop()
            self.class_scope.pop()

    def visit_FunctionDef(self, n):
        self._make(n)
        self.scope.append(n.name)
        try:
            self.generic_visit(n)
        finally:
            self.scope.pop()

    def visit_AsyncFunctionDef(self, n):
        self._make(n)
        self.scope.append(n.name)
        try:
            self.generic_visit(n)
        finally:
            self.scope.pop()


# =========================================================
# RECOVERY (BLOCK BASED)
# =========================================================
def _blocks(src: str):
    lines = src.splitlines(keepends=True)
    out = []

    i = 0
    while i < len(lines):
        l = lines[i].lstrip()
        if not l.startswith(("def ", "async def ", "class ")):
            i += 1
            continue

        start = i
        indent = len(lines[i]) - len(lines[i].lstrip())
        j = i + 1

        while j < len(lines):
            nl = lines[j]
            if nl.strip():
                ni = len(nl) - len(nl.lstrip())
                if ni <= indent:
                    break
            j += 1

        out.append("".join(lines[start:j]))
        i = j

    return out


# =========================================================
# VALIDATION
# =========================================================
def _top_level_function_nodes(tree: ast.Module) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    return [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]


def _top_level_non_function_nodes(tree: ast.Module) -> list[ast.AST]:
    return [
        node
        for node in tree.body
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]


def validate_single_top_level_function_code(
    source_code: str,
    *,
    expected_name: str | None = None,
    allow_async: bool = True,
    allow_other_top_level_nodes: bool = False,
) -> dict[str, Any]:
    """
    Kodun modül seviyesinde tam olarak bir fonksiyon içerip içermediğini doğrular.

    KURALLAR:
    - Nested fonksiyonlar serbesttir
    - Top-level fonksiyon sayısı tam 1 olmalıdır
    - İstenirse beklenen fonksiyon adı kontrol edilir
    - İstenirse top-level başka node'lar yasaklanır

    Returns:
        {
            "valid": bool,
            "error_code": str,
            "message": str,
            "function_name": str,
            "function_kind": str,
            "top_level_function_count": int,
            "top_level_other_count": int,
        }
    """
    src = _normalize_text(source_code)

    if not src.strip():
        return {
            "valid": False,
            "error_code": "validation_error_code_empty",
            "message": "Kod boş.",
            "function_name": "",
            "function_kind": "",
            "top_level_function_count": 0,
            "top_level_other_count": 0,
        }

    try:
        tree = ast.parse(src, filename="<validation>")
    except SyntaxError as exc:
        satir = _i(getattr(exc, "lineno", 0))
        sutun = _i(getattr(exc, "offset", 0))
        mesaj = str(getattr(exc, "msg", "") or str(exc))
        return {
            "valid": False,
            "error_code": "validation_error_syntax_prefix",
            "message": (
                f"Syntax error: line {satir}, column {sutun} -> {mesaj}"
            ),
            "function_name": "",
            "function_kind": "",
            "top_level_function_count": 0,
            "top_level_other_count": 0,
        }
    except Exception as exc:
        return {
            "valid": False,
            "error_code": "validation_error",
            "message": str(exc),
            "function_name": "",
            "function_kind": "",
            "top_level_function_count": 0,
            "top_level_other_count": 0,
        }

    funcs = _top_level_function_nodes(tree)
    others = _top_level_non_function_nodes(tree)

    if len(funcs) != 1:
        return {
            "valid": False,
            "error_code": "validation_error_single_function_required",
            "message": "Yeni kod tam olarak tek bir top-level fonksiyon içermelidir.",
            "function_name": "",
            "function_kind": "",
            "top_level_function_count": len(funcs),
            "top_level_other_count": len(others),
        }

    node = funcs[0]
    func_name = str(getattr(node, "name", "") or "").strip()
    func_kind = "async_function" if isinstance(node, ast.AsyncFunctionDef) else "function"

    if not allow_async and isinstance(node, ast.AsyncFunctionDef):
        return {
            "valid": False,
            "error_code": "validation_error_only_def_allowed",
            "message": "Async fonksiyon bu akışta desteklenmiyor.",
            "function_name": func_name,
            "function_kind": func_kind,
            "top_level_function_count": len(funcs),
            "top_level_other_count": len(others),
        }

    if not allow_other_top_level_nodes and others:
        return {
            "valid": False,
            "error_code": "validation_error_only_def_allowed",
            "message": "Top-level düzeyde yalnızca tek fonksiyon bulunmalıdır.",
            "function_name": func_name,
            "function_kind": func_kind,
            "top_level_function_count": len(funcs),
            "top_level_other_count": len(others),
        }

    beklenen = str(expected_name or "").strip()
    if beklenen and func_name != beklenen:
        return {
            "valid": False,
            "error_code": "selection_error_title",
            "message": (
                f"Beklenen fonksiyon adı '{beklenen}', gelen fonksiyon adı '{func_name}'."
            ),
            "function_name": func_name,
            "function_kind": func_kind,
            "top_level_function_count": len(funcs),
            "top_level_other_count": len(others),
        }

    return {
        "valid": True,
        "error_code": "",
        "message": "",
        "function_name": func_name,
        "function_kind": func_kind,
        "top_level_function_count": len(funcs),
        "top_level_other_count": len(others),
    }


# =========================================================
# CORE
# =========================================================
def _scan_full(src: str, fp: str):
    tree = ast.parse(src)
    ctx = _Ctx(src)
    col = _Collector(ctx, fp)
    col.visit(tree)
    return sorted(col.items, key=lambda x: (x.lineno, x.path))


def _scan_recovery(src: str, fp: str):
    ctx = _Ctx(src)
    col = _Collector(ctx, fp)

    for b in _blocks(src):
        try:
            mod = ast.parse(b)
        except Exception:
            continue

        for n in mod.body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                col.visit(n)

    return sorted(col.items, key=lambda x: (x.lineno, x.path))


# =========================================================
# PUBLIC
# =========================================================
def scan_functions_from_code(
    source_code: str,
    file_path: str = "<memory>",
) -> List[FunctionItem]:
    src = _normalize_text(source_code)

    if not src.strip():
        return []

    try:
        return _scan_full(src, file_path)
    except SyntaxError as e:
        res = _scan_recovery(src, file_path)
        if res:
            return res
        raise FunctionScanError(
            f"Parse hatası: satır {e.lineno}, sütun {e.offset}"
        )


def scan_functions_from_file(file_path: str | Path) -> List[FunctionItem]:
    path = _normalize_path(file_path)

    try:
        if not path.exists():
            raise FunctionScanError(f"Dosya yok: {path}")
        if not path.is_file():
            raise FunctionScanError(f"Dosya değil: {path}")

        txt = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise FunctionScanError("UTF-8 değil")
    except OSError:
        raise FunctionScanError("Dosya okunamadı")

    try:
        fp = str(path.resolve())
    except Exception:
        fp = str(path)

    return scan_functions_from_code(txt, file_path=fp)


__all__ = (
    "FunctionScanError",
    "scan_functions_from_code",
    "scan_functions_from_file",
    "validate_single_top_level_function_code",
)