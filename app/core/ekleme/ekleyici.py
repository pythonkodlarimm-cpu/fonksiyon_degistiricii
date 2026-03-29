# -*- coding: utf-8 -*-
"""
DOSYA: app/core/ekleme/ekleyici.py

ROL:
- Fonksiyon ekleme motoru
- Duplicate fonksiyon kontrolü
- Import auto-add (AST tabanlı, lazy-aware)
- Smart insert (AST body listesi üzerinden)
- Dosya üstü güvenli yazma ve motor bazlı yedekleme

MİMARİ:
- String satır kaydırma yerine AST üzerinde çalışır
- Hedef fonksiyonu path ile çözer
- after / before / inside_class / end_of_file modlarını güvenli biçimde uygular
- Importları ayrı işler, fonksiyon gövdesi ile karıştırmaz
- Final kodu ast.unparse ile üretir ve yeniden parse ederek doğrular
- Dosya yazımı atomik yapılır
- Yedekler motor bazlı klasöre yazılır

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Saf Python çalışır
- Pydroid3 / masaüstü / test ortamlarında aynı mantıkla davranır

SURUM: 13
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

import ast
import copy
import os
import shutil
import textwrap
from pathlib import Path
from typing import Final, Iterable, TypeAlias

from app.core.modeller.modeller import FunctionItem
from app.core.yedekleme.yollar import backup_dosya_yolu_uret


FunctionNode: TypeAlias = ast.FunctionDef | ast.AsyncFunctionDef
StatementNode: TypeAlias = ast.stmt

MODE_AFTER: Final[str] = "after"
MODE_BEFORE: Final[str] = "before"
MODE_INSIDE_CLASS: Final[str] = "inside_class"
MODE_END_OF_FILE: Final[str] = "end_of_file"

ALLOWED_MODES: Final[frozenset[str]] = frozenset(
    {
        MODE_AFTER,
        MODE_BEFORE,
        MODE_INSIDE_CLASS,
        MODE_END_OF_FILE,
    }
)


class FunctionInsertError(ValueError):
    """
    Fonksiyon ekleme sürecinde oluşan kontrollü hata.
    """


# =========================================================
# NORMALIZE
# =========================================================
def _normalize_text(text: str) -> str:
    return str(text or "").replace("\r\n", "\n").replace("\r", "\n")


def _dedent_raw(code: str) -> str:
    return textwrap.dedent(str(code or "")).strip()


# =========================================================
# PARSE / VALIDATION
# =========================================================
def _parse_module(source_code: str) -> ast.Module:
    try:
        return ast.parse(source_code)
    except SyntaxError as exc:
        raise FunctionInsertError("Kaynak parse edilemedi.") from exc


def _validate_mode(mode: str) -> str:
    normalized = str(mode or "").strip().lower()

    if normalized not in ALLOWED_MODES:
        raise FunctionInsertError(
            f"Geçersiz mode: {mode!r}. Desteklenen modlar: {sorted(ALLOWED_MODES)}"
        )

    return normalized


def _clone_statement_nodes(
    nodes: Iterable[StatementNode],
) -> list[StatementNode]:
    return [copy.deepcopy(node) for node in nodes]


# =========================================================
# NEW CODE ANALYSIS
# =========================================================
def _split_new_code(
    code: str,
) -> tuple[list[StatementNode], list[FunctionNode]]:
    """
    Yeni kodu parse eder.

    Dönüş:
    - import node listesi
    - function node listesi

    Kural:
    - top-level import ve top-level function dışında node kabul edilmez
    """
    normalized = _dedent_raw(code)

    if not normalized:
        raise FunctionInsertError("Kod boş.")

    try:
        tree = ast.parse(normalized)
    except SyntaxError as exc:
        raise FunctionInsertError("Yeni kod parse edilemedi.") from exc

    import_nodes: list[StatementNode] = []
    function_nodes: list[FunctionNode] = []

    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            import_nodes.append(node)
            continue

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            function_nodes.append(node)
            continue

        raise FunctionInsertError(
            "Yeni kod yalnızca import ve fonksiyon tanımı içermelidir."
        )

    if not function_nodes:
        raise FunctionInsertError("Yeni kod içinde fonksiyon bulunamadı.")

    return import_nodes, function_nodes


def _extract_function_names_from_new_code(code: str) -> list[str]:
    _, function_nodes = _split_new_code(code)
    return [node.name for node in function_nodes]


# =========================================================
# DUPLICATE CHECK
# =========================================================
def _collect_existing_function_names(source_code: str) -> set[str]:
    tree = _parse_module(source_code)
    result: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            result.add(node.name)

    return result


def _check_duplicate_functions(source_code: str, new_code: str) -> None:
    existing_names = _collect_existing_function_names(source_code)
    new_names = _extract_function_names_from_new_code(new_code)

    for name in new_names:
        if name in existing_names:
            raise FunctionInsertError(f"{name!r} zaten mevcut.")


# =========================================================
# IMPORT HANDLING
# =========================================================
def _import_node_key(node: ast.AST) -> tuple:
    if isinstance(node, ast.Import):
        return (
            "import",
            tuple((alias.name, alias.asname) for alias in node.names),
        )

    if isinstance(node, ast.ImportFrom):
        return (
            "from",
            node.module,
            int(node.level or 0),
            tuple((alias.name, alias.asname) for alias in node.names),
        )

    raise FunctionInsertError("Geçersiz import node tipi.")


def _collect_existing_import_keys(module: ast.Module) -> set[tuple]:
    """
    ast.walk kullanıldığı için lazy importlar da görülür.
    """
    result: set[tuple] = set()

    for node in ast.walk(module):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            result.add(_import_node_key(node))

    return result


def _top_level_import_insert_index(module: ast.Module) -> int:
    """
    Top-level import ekleme noktasını döndürür.

    Korur:
    - modül docstring'i
    - mevcut top-level import bloğu
    """
    body = module.body
    index = 0

    if body:
        first = body[0]
        if (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
        ):
            index = 1

    while index < len(body) and isinstance(body[index], (ast.Import, ast.ImportFrom)):
        index += 1

    return index


def _insert_top_level_imports(
    module: ast.Module,
    import_nodes: Iterable[StatementNode],
) -> None:
    existing_import_keys = _collect_existing_import_keys(module)
    insert_index = _top_level_import_insert_index(module)

    for node in import_nodes:
        key = _import_node_key(node)

        if key in existing_import_keys:
            continue

        module.body.insert(insert_index, copy.deepcopy(node))
        existing_import_keys.add(key)
        insert_index += 1


# =========================================================
# TARGET RESOLVE
# =========================================================
class _TargetResolver(ast.NodeVisitor):
    """
    Hedef function path'ini AST içinde çözer.

    Bulduğu anda şu alanları doldurur:
    - target_node
    - target_parent_body
    - target_index
    - enclosing_class_node
    """

    def __init__(self, target: FunctionItem) -> None:
        self.target = target
        self.scope: list[str] = []
        self.class_stack: list[ast.ClassDef] = []

        self.target_node: FunctionNode | None = None
        self.target_parent_body: list[StatementNode] | None = None
        self.target_index: int | None = None
        self.enclosing_class_node: ast.ClassDef | None = None

    def _current_path(self, name: str) -> str:
        return ".".join(self.scope + [name])

    def _scan_body(self, body: list[StatementNode]) -> None:
        for index, node in enumerate(body):
            if self.target_node is not None:
                return

            if isinstance(node, ast.ClassDef):
                self.visit_ClassDef(node)
                continue

            if isinstance(node, ast.FunctionDef):
                current_path = self._current_path(node.name)

                if current_path == self.target.path:
                    self.target_node = node
                    self.target_parent_body = body
                    self.target_index = index
                    self.enclosing_class_node = (
                        self.class_stack[-1] if self.class_stack else None
                    )
                    return

                self.scope.append(node.name)
                try:
                    self._scan_body(node.body)
                finally:
                    self.scope.pop()
                continue

            if isinstance(node, ast.AsyncFunctionDef):
                current_path = self._current_path(node.name)

                if current_path == self.target.path:
                    self.target_node = node
                    self.target_parent_body = body
                    self.target_index = index
                    self.enclosing_class_node = (
                        self.class_stack[-1] if self.class_stack else None
                    )
                    return

                self.scope.append(node.name)
                try:
                    self._scan_body(node.body)
                finally:
                    self.scope.pop()
                continue

    def visit_Module(self, node: ast.Module) -> None:
        self._scan_body(node.body)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.scope.append(node.name)
        self.class_stack.append(node)

        try:
            self._scan_body(node.body)
        finally:
            self.class_stack.pop()
            self.scope.pop()


def _resolve_target(module: ast.Module, target: FunctionItem) -> _TargetResolver:
    resolver = _TargetResolver(target)
    resolver.visit(module)

    if (
        resolver.target_node is None
        or resolver.target_parent_body is None
        or resolver.target_index is None
    ):
        raise FunctionInsertError("Hedef bulunamadı.")

    return resolver


# =========================================================
# AST INSERT
# =========================================================
def _insert_after_target(
    resolver: _TargetResolver,
    function_nodes: list[FunctionNode],
) -> None:
    parent_body = resolver.target_parent_body
    target_index = resolver.target_index

    if parent_body is None or target_index is None:
        raise FunctionInsertError("after insert çözümlenemedi.")

    parent_body[target_index + 1 : target_index + 1] = _clone_statement_nodes(
        function_nodes
    )


def _insert_before_target(
    resolver: _TargetResolver,
    function_nodes: list[FunctionNode],
) -> None:
    parent_body = resolver.target_parent_body
    target_index = resolver.target_index

    if parent_body is None or target_index is None:
        raise FunctionInsertError("before insert çözümlenemedi.")

    parent_body[target_index:target_index] = _clone_statement_nodes(function_nodes)


def _insert_inside_class(
    resolver: _TargetResolver,
    function_nodes: list[FunctionNode],
) -> None:
    class_node = resolver.enclosing_class_node

    if class_node is None:
        raise FunctionInsertError("Hedef bir class içinde değil.")

    class_node.body.extend(_clone_statement_nodes(function_nodes))


def _insert_end_of_file(
    module: ast.Module,
    function_nodes: list[FunctionNode],
) -> None:
    module.body.extend(_clone_statement_nodes(function_nodes))


# =========================================================
# FINALIZE
# =========================================================
def _unparse_module(module: ast.Module) -> str:
    ast.fix_missing_locations(module)

    try:
        result = ast.unparse(module)
    except Exception as exc:
        raise FunctionInsertError("Kod üretilemedi.") from exc

    try:
        ast.parse(result)
    except SyntaxError as exc:
        raise FunctionInsertError("Syntax bozuldu.") from exc

    return result


# =========================================================
# FILE HELPERS
# =========================================================
def _build_backup_path(path_obj: Path) -> Path:
    """
    Motor bazlı Android uyumlu backup dosya yolu üretir.
    """
    return backup_dosya_yolu_uret(
        motor_adi="ekleme",
        kaynak_dosya_adi=path_obj.name,
        uzanti=".bak",
    )


def _build_temp_path(path_obj: Path) -> Path:
    """
    Atomik yazma için geçici dosya yolu üretir.
    """
    return path_obj.with_suffix(path_obj.suffix + ".tmp")


def _safe_remove(path_obj: Path) -> None:
    """
    Dosya varsa sessizce silmeyi dener.
    """
    try:
        if path_obj.exists():
            path_obj.unlink()
    except Exception:
        pass


# =========================================================
# MAIN ENGINE
# =========================================================
def insert_function(
    source_code: str,
    target: FunctionItem | None,
    new_code: str,
    *,
    mode: str,
) -> str:
    """
    Kaynak koda yeni fonksiyon ekler.

    mode:
    - after
    - before
    - inside_class
    - end_of_file
    """
    normalized_source = _normalize_text(source_code)
    normalized_mode = _validate_mode(mode)

    _check_duplicate_functions(normalized_source, new_code)

    module = _parse_module(normalized_source)
    import_nodes, function_nodes = _split_new_code(new_code)

    _insert_top_level_imports(module, import_nodes)

    if normalized_mode == MODE_END_OF_FILE:
        _insert_end_of_file(module, function_nodes)
    else:
        if target is None:
            raise FunctionInsertError("target gerekli.")

        resolver = _resolve_target(module, target)

        if normalized_mode == MODE_AFTER:
            _insert_after_target(resolver, function_nodes)
        elif normalized_mode == MODE_BEFORE:
            _insert_before_target(resolver, function_nodes)
        elif normalized_mode == MODE_INSIDE_CLASS:
            _insert_inside_class(resolver, function_nodes)
        else:
            raise FunctionInsertError(f"Geçersiz mode: {mode}")

    return _unparse_module(module)


def insert_function_in_file(
    file_path: str,
    target: FunctionItem | None,
    new_code: str,
    *,
    mode: str,
    backup: bool = True,
    encoding: str = "utf-8",
) -> str:
    """
    Dosya içindeki kaynak koda yeni fonksiyon ekler, gerekirse yedek alır
    ve sonucu atomik biçimde dosyaya yazar.
    """
    raw_path = str(file_path or "").strip()
    if not raw_path:
        raise FunctionInsertError("Dosya yolu boş.")

    path = Path(raw_path)

    if not path.exists():
        raise FunctionInsertError("Dosya yok.")

    if not path.is_file():
        raise FunctionInsertError("Geçerli bir dosya değil.")

    try:
        source_code = path.read_text(encoding=encoding)
    except UnicodeDecodeError as exc:
        raise FunctionInsertError(f"Dosya '{encoding}' ile okunamadı.") from exc
    except OSError as exc:
        raise FunctionInsertError("Dosya okunamadı.") from exc

    updated = insert_function(
        source_code=source_code,
        target=target,
        new_code=new_code,
        mode=mode,
    )

    if backup:
        backup_path = _build_backup_path(path)
        try:
            shutil.copyfile(path, backup_path)
        except Exception as exc:
            raise FunctionInsertError(
                f"Yedek dosya oluşturulamadı: {backup_path}"
            ) from exc

    temp_path = _build_temp_path(path)

    try:
        temp_path.write_text(updated, encoding=encoding)
        os.replace(str(temp_path), str(path))
    except Exception as exc:
        _safe_remove(temp_path)
        raise FunctionInsertError("Güncellenmiş dosya yazılamadı.") from exc

    return updated