# -*- coding: utf-8 -*-
"""
DOSYA: app/core/degistirme/degistirici.py

ROL:
- Fonksiyon değiştirmenin çekirdeği
- AST tabanlı doğru hedef bulma
- Deterministik ve güvenli replace
- Android uyumlu yedekleme entegrasyonu
- Yeni fonksiyon kodu için top-level doğrulama sağlar

GARANTI:
- Deep nested destekler
- Sadece hedef fonksiyon değişir
- Syntax kırılmaz
- Dosya yazımı atomik yapılır
- Yedekler motor bazlı klasöre yazılır
- Nested fonksiyonlar yeni kod içinde serbesttir
- Modül seviyesinde tek fonksiyon doğrulaması yapılabilir

MİMARİ:
- Saf Python
- AST tabanlı hedef çözümleme
- Text replace yerine satır aralığı bazlı kontrollü güncelleme
- Fail-soft temp temizliği
- Yedek yolu app/core/yedekleme/yollar.py üzerinden üretilir
- Deterministik API
- Geriye uyumluluk katmanı içermez

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Pydroid3 / masaüstü / test ortamlarında aynı mantıkla davranır

SURUM: 5
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

import ast
import os
import shutil
import textwrap
from pathlib import Path
from typing import Final, TypedDict, cast

from app.core.modeller.modeller import FunctionItem
from app.core.yedekleme.yollar import backup_dosya_yolu_uret

_ALLOWED_DEF_PREFIXES: Final[tuple[str, ...]] = ("def ", "async def ")
_TMP_SUFFIX: Final[str] = ".tmp"


# =========================================================
# ERROR
# =========================================================
class FunctionReplaceError(ValueError):
    """
    Fonksiyon değiştirme sırasında oluşan kontrollü hata.
    """


class FunctionCodeValidationResult(TypedDict):
    """
    Yeni fonksiyon kodu doğrulama sonucu.
    """

    valid: bool
    error_code: str
    message: str
    function_name: str
    function_kind: str
    top_level_function_count: int
    top_level_other_count: int


# =========================================================
# NORMALIZE
# =========================================================
def _norm(text: str) -> str:
    """
    Satır sonlarını normalize eder.
    """
    return str(text or "").replace("\r\n", "\n").replace("\r", "\n")


def _strip(text: str) -> str:
    """
    Baş ve sondaki boş satırları temizler.
    """
    lines = _norm(text).split("\n")

    while lines and not lines[0].strip():
        lines.pop(0)

    while lines and not lines[-1].strip():
        lines.pop()

    return "\n".join(lines)


def _dedent(text: str) -> str:
    """
    Yeni fonksiyon kodunu normalize edip soldan ortak girintiyi kaldırır.
    """
    cleaned = _strip(text)

    if not cleaned:
        raise FunctionReplaceError("Yeni kod boş.")

    return textwrap.dedent(cleaned)


def _normalize_file_path(file_path: str | Path) -> Path:
    """
    Dosya yolunu doğrular ve Path nesnesine çevirir.
    """
    raw_path = str(file_path or "").strip()
    if not raw_path:
        raise FunctionReplaceError("Dosya yolu boş.")
    return Path(raw_path)


# =========================================================
# AST
# =========================================================
def _parse(source: str) -> ast.Module:
    """
    Kaynak kodu AST'e çevirir.
    """
    try:
        return ast.parse(source)
    except SyntaxError as exc:
        raise FunctionReplaceError("Kaynak parse edilemedi.") from exc


def _top_level_function_nodes(
    tree: ast.Module,
) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    """
    Modül seviyesindeki fonksiyon düğümlerini döndürür.
    """
    return [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]


def _top_level_non_function_nodes(tree: ast.Module) -> list[ast.AST]:
    """
    Modül seviyesinde fonksiyon olmayan düğümleri döndürür.
    """
    return [
        node
        for node in tree.body
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]


# =========================================================
# VALIDATION
# =========================================================
def validate_single_top_level_function_code(
    source_code: str,
    *,
    expected_name: str | None = None,
    allow_async: bool = True,
    allow_other_top_level_nodes: bool = False,
) -> FunctionCodeValidationResult:
    """
    Kodun modül seviyesinde tam olarak bir fonksiyon içerip içermediğini doğrular.

    Kurallar:
    - Nested fonksiyonlar serbesttir
    - Top-level fonksiyon sayısı tam 1 olmalıdır
    - İstenirse beklenen fonksiyon adı doğrulanır
    - İstenirse top-level başka node'lar yasaklanır
    """
    src = _norm(source_code)

    if not src.strip():
        return FunctionCodeValidationResult(
            valid=False,
            error_code="validation_error_code_empty",
            message="Kod boş.",
            function_name="",
            function_kind="",
            top_level_function_count=0,
            top_level_other_count=0,
        )

    try:
        tree = ast.parse(src, filename="<validation>")
    except SyntaxError as exc:
        line = int(getattr(exc, "lineno", 0) or 0)
        column = int(getattr(exc, "offset", 0) or 0)
        msg = str(getattr(exc, "msg", "") or str(exc))
        return FunctionCodeValidationResult(
            valid=False,
            error_code="validation_error_syntax_prefix",
            message=f"Syntax error: line {line}, column {column} -> {msg}",
            function_name="",
            function_kind="",
            top_level_function_count=0,
            top_level_other_count=0,
        )
    except Exception as exc:
        return FunctionCodeValidationResult(
            valid=False,
            error_code="validation_error",
            message=str(exc),
            function_name="",
            function_kind="",
            top_level_function_count=0,
            top_level_other_count=0,
        )

    funcs = _top_level_function_nodes(tree)
    others = _top_level_non_function_nodes(tree)

    if len(funcs) != 1:
        return FunctionCodeValidationResult(
            valid=False,
            error_code="validation_error_single_function_required",
            message="Yeni kod tam olarak tek bir top-level fonksiyon içermelidir.",
            function_name="",
            function_kind="",
            top_level_function_count=len(funcs),
            top_level_other_count=len(others),
        )

    node = funcs[0]
    function_name = str(getattr(node, "name", "") or "").strip()
    function_kind = (
        "async_function" if isinstance(node, ast.AsyncFunctionDef) else "function"
    )

    if not allow_async and isinstance(node, ast.AsyncFunctionDef):
        return FunctionCodeValidationResult(
            valid=False,
            error_code="validation_error_only_def_allowed",
            message="Async fonksiyon bu akışta desteklenmiyor.",
            function_name=function_name,
            function_kind=function_kind,
            top_level_function_count=len(funcs),
            top_level_other_count=len(others),
        )

    if not allow_other_top_level_nodes and others:
        return FunctionCodeValidationResult(
            valid=False,
            error_code="validation_error_only_def_allowed",
            message="Top-level düzeyde yalnızca tek fonksiyon bulunmalıdır.",
            function_name=function_name,
            function_kind=function_kind,
            top_level_function_count=len(funcs),
            top_level_other_count=len(others),
        )

    expected = str(expected_name or "").strip()
    if expected and function_name != expected:
        return FunctionCodeValidationResult(
            valid=False,
            error_code="selection_error_title",
            message=(
                f"Beklenen fonksiyon adı '{expected}', "
                f"gelen fonksiyon adı '{function_name}'."
            ),
            function_name=function_name,
            function_kind=function_kind,
            top_level_function_count=len(funcs),
            top_level_other_count=len(others),
        )

    return FunctionCodeValidationResult(
        valid=True,
        error_code="",
        message="",
        function_name=function_name,
        function_kind=function_kind,
        top_level_function_count=len(funcs),
        top_level_other_count=len(others),
    )


# =========================================================
# FINDER
# =========================================================
class _Finder(ast.NodeVisitor):
    """
    Hedef FunctionItem'a karşılık gelen AST fonksiyon düğümünü bulur.
    """

    __slots__ = ("target", "scope", "class_stack", "node")

    def __init__(self, target: FunctionItem) -> None:
        self.target = target
        self.scope: list[str] = []
        self.class_stack: list[str] = []
        self.node: ast.FunctionDef | ast.AsyncFunctionDef | None = None

    def _kind(self, node: ast.AST) -> str:
        async_ = isinstance(node, ast.AsyncFunctionDef)
        in_class = bool(self.class_stack)
        nested = bool(self.scope)

        if in_class and nested:
            return "async_nested" if async_ else "nested"

        if in_class:
            return "async_method" if async_ else "method"

        if nested:
            return "async_nested" if async_ else "nested"

        return "async_function" if async_ else "function"

    def _match(self, node: ast.AST) -> bool:
        name = getattr(node, "name", "")
        path = ".".join(self.scope + [name]) if self.scope else name
        lineno = getattr(node, "lineno", None)

        return (
            path == self.target.path
            and lineno == self.target.lineno
            and self._kind(node) == self.target.kind
        )

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if self.node is not None:
            return

        self.scope.append(node.name)
        self.class_stack.append(node.name)

        try:
            for child in node.body:
                self.visit(child)
        finally:
            self.class_stack.pop()
            self.scope.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if self.node is not None:
            return

        if self._match(node):
            self.node = node
            return

        self.scope.append(node.name)

        try:
            for child in node.body:
                self.visit(child)
        finally:
            self.scope.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        if self.node is not None:
            return

        if self._match(node):
            self.node = node
            return

        self.scope.append(node.name)

        try:
            for child in node.body:
                self.visit(child)
        finally:
            self.scope.pop()


# =========================================================
# RANGE
# =========================================================
def _resolve_range(source: str, target: FunctionItem) -> tuple[int, int]:
    """
    Hedef fonksiyonun kaynak içindeki satır aralığını çözer.

    Dönüş:
    - start: 0-index başlangıç
    - end: 0-index dışlayıcı bitiş
    """
    tree = _parse(source)

    finder = _Finder(target)
    finder.visit(tree)

    if finder.node is None:
        raise FunctionReplaceError("Fonksiyon bulunamadı.")

    node = finder.node
    end_lineno = getattr(node, "end_lineno", None)

    if end_lineno is None:
        raise FunctionReplaceError("Fonksiyon bitiş satırı çözülemedi.")

    return int(node.lineno) - 1, int(end_lineno)


# =========================================================
# PREPARE
# =========================================================
def _prepare(target: FunctionItem, code: str) -> str:
    """
    Yeni fonksiyon kodunu hedef girinti seviyesine taşır.
    """
    prepared_code = _dedent(code)

    validation = validate_single_top_level_function_code(
        prepared_code,
        expected_name=target.name,
        allow_async=True,
        allow_other_top_level_nodes=False,
    )

    if not validation["valid"]:
        raise FunctionReplaceError(validation["message"] or "Yeni kod doğrulanamadı.")

    if not prepared_code.lstrip().startswith(_ALLOWED_DEF_PREFIXES):
        raise FunctionReplaceError("Kod 'def' veya 'async def' ile başlamalıdır.")

    indent = " " * int(target.col_offset)
    lines = prepared_code.splitlines()
    out: list[str] = []

    for line in lines:
        if line.strip():
            out.append(indent + line)
        else:
            out.append("")

    return "\n".join(out) + "\n"


# =========================================================
# FILE HELPERS
# =========================================================
def _build_backup_path(path_obj: Path) -> Path:
    """
    Motor bazlı Android uyumlu backup dosya yolu üretir.
    """
    return backup_dosya_yolu_uret(
        motor_adi="degistirme",
        kaynak_dosya_adi=path_obj.name,
        uzanti=".bak",
    )


def _build_temp_path(path_obj: Path) -> Path:
    """
    Atomik yazma için geçici dosya yolu üretir.
    """
    return path_obj.with_suffix(path_obj.suffix + _TMP_SUFFIX)


def _safe_remove(path_obj: Path) -> None:
    """
    Dosya varsa sessizce silmeyi dener.
    """
    try:
        if path_obj.exists():
            path_obj.unlink()
    except Exception:
        pass


def _read_utf8_text(path_obj: Path) -> str:
    """
    UTF-8 olarak dosya okur.
    """
    try:
        return path_obj.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise FunctionReplaceError("Dosya utf-8 olarak okunamadı.") from exc
    except OSError as exc:
        raise FunctionReplaceError("Dosya okunamadı.") from exc


def _write_utf8_text_atomic(path_obj: Path, content: str) -> None:
    """
    İçeriği atomik olarak dosyaya yazar.
    """
    tmp_path = _build_temp_path(path_obj)

    try:
        tmp_path.write_text(content, encoding="utf-8")
        os.replace(str(tmp_path), str(path_obj))
    except Exception as exc:
        _safe_remove(tmp_path)
        raise FunctionReplaceError("Güncellenmiş dosya yazılamadı.") from exc


# =========================================================
# CORE REPLACE
# =========================================================
def update_function_in_code(
    source_code: str,
    target_item: FunctionItem,
    new_code: str,
) -> str:
    """
    Kaynak kod içinde yalnızca hedef fonksiyonu değiştirir.
    """
    source = _norm(source_code)

    start, end = _resolve_range(source, target_item)
    prepared = _prepare(target_item, new_code)

    lines = source.splitlines(keepends=True)
    new_lines = prepared.splitlines(keepends=True)

    lines[start:end] = new_lines
    result = "".join(lines)

    try:
        ast.parse(result)
    except SyntaxError as exc:
        raise FunctionReplaceError("Syntax bozuldu.") from exc

    return result


# =========================================================
# FILE
# =========================================================
def update_function_in_file(
    file_path: str,
    target_item: FunctionItem,
    new_code: str,
    *,
    backup: bool = True,
) -> str:
    """
    Dosya içindeki hedef fonksiyonu günceller, gerekirse yedek alır
    ve sonucu atomik biçimde dosyaya yazar.
    """
    path = _normalize_file_path(file_path)

    if not path.exists():
        raise FunctionReplaceError("Dosya yok.")

    if not path.is_file():
        raise FunctionReplaceError("Geçerli bir dosya değil.")

    source = _read_utf8_text(path)

    updated = update_function_in_code(
        source_code=source,
        target_item=target_item,
        new_code=new_code,
    )

    if backup:
        backup_path = _build_backup_path(path)
        try:
            shutil.copyfile(path, backup_path)
        except Exception as exc:
            raise FunctionReplaceError(
                f"Yedek dosya oluşturulamadı: {backup_path}"
            ) from exc

    _write_utf8_text_atomic(path, updated)
    return updated


__all__ = (
    "FunctionReplaceError",
    "FunctionCodeValidationResult",
    "validate_single_top_level_function_code",
    "update_function_in_code",
    "update_function_in_file",
)