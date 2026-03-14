# -*- coding: utf-8 -*-
"""
DOSYA: app/core/degistirici.py

ROL:
- Seçilen fonksiyonun kaynak kod içinde güvenli biçimde değiştirilmesi
- Tek fonksiyonluk yeni kodun doğrulanması
- Girintinin hedef bloğa göre uyarlanması
- Güncelleme sonrası sözdizimi kontrolü
- Dosya üstünde güvenli yazma + yedek alma

HEDEF:
- Yanlış satır aralığına yazmayı azaltmak
- Async / normal fonksiyon uyumluluğunu korumak
- Nested function ve method senaryolarında daha güvenli davranmak

GÜÇLENDİRME:
- target_item doğrulama
- hedef blok gerçekten seçili öğe mi kontrolü
- satır kayması durumunda yakın blok bulma
- yedek çakışırsa zaman damgalı yedek üretme
- dosya yazma öncesi daha güvenli kontroller
- Android / APK ortamında daha güvenli yazma akışı
"""

from __future__ import annotations

import ast
import os
import shutil
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.core.modeller import FunctionItem


class FunctionReplaceError(ValueError):
    """Fonksiyon değiştirme sırasında oluşan kontrollü hata."""


def _normalize_text(text: str) -> str:
    s = str(text or "")
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = s.replace("\t", "    ")
    return s


def _strip_outer_blank_lines(text: str) -> str:
    lines = _normalize_text(text).split("\n")

    while lines and not lines[0].strip():
        lines.pop(0)

    while lines and not lines[-1].strip():
        lines.pop()

    return "\n".join(lines)


def _ensure_trailing_newline(text: str) -> str:
    s = _normalize_text(text)
    if not s.endswith("\n"):
        s += "\n"
    return s


def _dedent_user_code(text: str) -> str:
    cleaned = _strip_outer_blank_lines(text)
    if not cleaned.strip():
        raise FunctionReplaceError("Yeni fonksiyon kodu boş olamaz.")
    return textwrap.dedent(cleaned)


def _validate_target_item(target_item: FunctionItem) -> None:
    if target_item is None:
        raise FunctionReplaceError("Hedef fonksiyon bilgisi boş.")

    name = str(getattr(target_item, "name", "") or "").strip()
    path = str(getattr(target_item, "path", "") or "").strip()
    kind = str(getattr(target_item, "kind", "") or "").strip()
    lineno = int(getattr(target_item, "lineno", 0) or 0)
    end_lineno = int(getattr(target_item, "end_lineno", 0) or 0)
    col_offset = int(getattr(target_item, "col_offset", 0) or 0)

    if not name:
        raise FunctionReplaceError("Hedef fonksiyon adı boş.")
    if not path:
        raise FunctionReplaceError("Hedef fonksiyon path alanı boş.")
    if kind not in {"function", "async_function"}:
        raise FunctionReplaceError(f"Geçersiz hedef fonksiyon türü: {kind!r}")
    if lineno <= 0:
        raise FunctionReplaceError(f"Geçersiz hedef başlangıç satırı: {lineno}")
    if end_lineno <= 0 or end_lineno < lineno:
        raise FunctionReplaceError(f"Geçersiz hedef bitiş satırı: {end_lineno}")
    if col_offset < 0:
        raise FunctionReplaceError(f"Geçersiz hedef girintisi: {col_offset}")


def _parse_single_function_module(code: str) -> ast.Module:
    try:
        module = ast.parse(code)
    except SyntaxError as exc:
        raise FunctionReplaceError(
            f"Yeni kod parse edilemedi: satır {exc.lineno}, sütun {exc.offset} -> {exc.msg}"
        ) from exc

    if not module.body:
        raise FunctionReplaceError("Yeni kod boş görünüyor.")

    if len(module.body) != 1:
        raise FunctionReplaceError("Yeni kod tam olarak tek bir fonksiyon içermelidir.")

    node = module.body[0]
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        raise FunctionReplaceError("Yeni kod yalnızca tek bir 'def' veya 'async def' içermelidir.")

    return module


def _get_single_function_node(module: ast.Module) -> ast.FunctionDef | ast.AsyncFunctionDef:
    node = module.body[0]
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        raise FunctionReplaceError("Yeni kod yalnızca tek bir 'def' veya 'async def' içermelidir.")
    return node


def _validate_kind_compatibility(target_item: FunctionItem, new_node: ast.AST) -> None:
    target_kind = str(getattr(target_item, "kind", "") or "").strip().lower()

    if target_kind == "async_function" and not isinstance(new_node, ast.AsyncFunctionDef):
        raise FunctionReplaceError("Seçilen hedef async fonksiyon. Yeni kod da 'async def' olmalıdır.")

    if target_kind == "function" and not isinstance(new_node, ast.FunctionDef):
        raise FunctionReplaceError("Seçilen hedef normal fonksiyon. Yeni kod da 'def' olmalıdır.")


def _validate_name_compatibility(
    target_item: FunctionItem,
    new_node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> None:
    target_name = str(getattr(target_item, "name", "") or "").strip()
    new_name = str(getattr(new_node, "name", "") or "").strip()

    if target_name and new_name and target_name != new_name:
        raise FunctionReplaceError(
            f"Fonksiyon adı uyuşmuyor. Seçili hedef: '{target_name}', yeni kod: '{new_name}'"
        )


def _indent_code_block(code: str, indent_spaces: int) -> str:
    code = _ensure_trailing_newline(code)
    lines = code.splitlines(keepends=True)

    if indent_spaces <= 0:
        return "".join(lines)

    prefix = " " * indent_spaces
    out: list[str] = []

    for line in lines:
        if line.strip():
            out.append(prefix + line)
        else:
            out.append(line)

    return "".join(out)


def _prepare_replacement_code(target_item: FunctionItem, new_code: str) -> str:
    _validate_target_item(target_item)

    normalized = _normalize_text(new_code)
    dedented = _dedent_user_code(normalized)

    if not dedented.lstrip().startswith(("def ", "async def ")):
        raise FunctionReplaceError("Yeni kod 'def' veya 'async def' ile başlamalıdır.")

    module = _parse_single_function_module(dedented)
    parsed_node = _get_single_function_node(module)

    _validate_kind_compatibility(target_item, parsed_node)
    _validate_name_compatibility(target_item, parsed_node)

    indented = _indent_code_block(dedented, int(target_item.col_offset))
    return _ensure_trailing_newline(indented)


def _validate_line_range(source_code: str, target_item: FunctionItem) -> tuple[int, int, list[str]]:
    lines = _normalize_text(source_code).splitlines(keepends=True)

    if not lines:
        raise FunctionReplaceError("Kaynak dosya boş.")

    start_index = int(target_item.lineno) - 1
    end_index = int(target_item.end_lineno)

    if start_index < 0 or start_index >= len(lines):
        raise FunctionReplaceError(
            f"Geçersiz başlangıç satırı: lineno={target_item.lineno}, toplam={len(lines)}"
        )

    if end_index < start_index + 1 or end_index > len(lines):
        raise FunctionReplaceError(
            f"Geçersiz bitiş satırı: end_lineno={target_item.end_lineno}, toplam={len(lines)}"
        )

    return start_index, end_index, lines


def _looks_like_target_function_header(line: str, target_item: FunctionItem) -> bool:
    stripped = str(line or "").lstrip()
    target_name = str(getattr(target_item, "name", "") or "").strip()

    if not target_name:
        return False

    return (
        stripped.startswith(f"def {target_name}(")
        or stripped.startswith(f"async def {target_name}(")
    )


def _extract_text_by_item_range(source_code: str, target_item: FunctionItem) -> str:
    start_index, end_index, lines = _validate_line_range(source_code, target_item)
    return "".join(lines[start_index:end_index])


def _normalize_for_compare(text: str) -> str:
    return _strip_outer_blank_lines(_normalize_text(text))


def _source_matches_target_item(source_code: str, target_item: FunctionItem) -> bool:
    try:
        current_block = _extract_text_by_item_range(source_code, target_item)
    except Exception:
        return False

    current_norm = _normalize_for_compare(current_block)
    target_norm = _normalize_for_compare(str(getattr(target_item, "source", "") or ""))

    if current_norm and target_norm and current_norm == target_norm:
        return True

    try:
        start_index, _end_index, lines = _validate_line_range(source_code, target_item)
        first_line = lines[start_index]
        if _looks_like_target_function_header(first_line, target_item):
            return True
    except Exception:
        pass

    return False


def _find_nearby_matching_range(
    source_code: str,
    target_item: FunctionItem,
    window: int = 8,
) -> Optional[tuple[int, int]]:
    """
    Satır kaymışsa, yakın çevrede aynı isimli ve benzer indentte fonksiyon başlığını arar.
    Dönüş: (new_start_index, new_end_index_exclusive)
    """
    lines = _normalize_text(source_code).splitlines(keepends=True)
    if not lines:
        return None

    expected_start = int(getattr(target_item, "lineno", 1) or 1) - 1
    expected_indent = int(getattr(target_item, "col_offset", 0) or 0)
    target_name = str(getattr(target_item, "name", "") or "").strip()
    target_kind = str(getattr(target_item, "kind", "") or "").strip()

    if not target_name:
        return None

    low = max(0, expected_start - window)
    high = min(len(lines) - 1, expected_start + window)

    if target_kind == "async_function":
        header_prefixes = [f"async def {target_name}("]
    elif target_kind == "function":
        header_prefixes = [f"def {target_name}("]
    else:
        header_prefixes = [f"def {target_name}(", f"async def {target_name}("]

    for idx in range(low, high + 1):
        raw = lines[idx]
        stripped = raw.lstrip()
        indent = len(raw) - len(stripped)

        if indent != expected_indent:
            continue

        if not any(stripped.startswith(prefix) for prefix in header_prefixes):
            continue

        end_index = idx + 1
        while end_index < len(lines):
            line = lines[end_index]
            if not line.strip():
                end_index += 1
                continue

            current_indent = len(line) - len(line.lstrip())
            if current_indent <= expected_indent:
                break
            end_index += 1

        return idx, end_index

    return None


def _validate_target_header(source_code: str, target_item: FunctionItem) -> tuple[int, int]:
    if _source_matches_target_item(source_code, target_item):
        start_index = int(target_item.lineno) - 1
        end_index = int(target_item.end_lineno)
        return start_index, end_index

    nearby = _find_nearby_matching_range(source_code, target_item, window=8)
    if nearby is not None:
        return nearby

    try:
        start_index, _end_index, lines = _validate_line_range(source_code, target_item)
        first_line = lines[start_index]

        if _looks_like_target_function_header(first_line, target_item):
            return start_index, int(target_item.end_lineno)
    except Exception:
        pass

    raise FunctionReplaceError(
        "Seçilen fonksiyon güncel kaynakta doğrulanamadı. "
        "Dosya değişmiş olabilir; lütfen yeniden tarayıp tekrar seçin."
    )


def _replace_line_range(
    source_code: str,
    target_item: FunctionItem,
    prepared_code: str,
) -> str:
    start_index, end_index = _validate_target_header(source_code, target_item)

    _dummy_start, _dummy_end, lines = _validate_line_range(
        source_code,
        FunctionItem(
            path=target_item.path,
            name=target_item.name,
            kind=target_item.kind,
            lineno=start_index + 1,
            end_lineno=end_index,
            col_offset=target_item.col_offset,
            end_col_offset=target_item.end_col_offset,
            signature=target_item.signature,
            source=target_item.source,
        ),
    )

    replacement_lines = prepared_code.splitlines(keepends=True)
    updated_lines = lines[:start_index] + replacement_lines + lines[end_index:]

    return "".join(updated_lines)


def _sanity_check_after_replace(updated_code: str) -> None:
    try:
        ast.parse(updated_code)
    except SyntaxError as exc:
        raise FunctionReplaceError(
            f"Güncelleme sonrası dosya sözdizimi bozuldu: satır {exc.lineno}, sütun {exc.offset} -> {exc.msg}"
        ) from exc


def update_function_in_code(
    source_code: str,
    target_item: FunctionItem,
    new_code: str,
) -> str:
    """
    Kaynak koddaki seçilen fonksiyonu yeni kod ile değiştirir.

    Özellikler:
    - nested function desteği
    - method içi nested function desteği
    - async / normal function tür kontrolü
    - hedef girintisine göre otomatik reindent
    - güncelleme sonrası AST parse kontrolü
    - hedef satırın gerçekten seçilen fonksiyona ait olduğunu doğrular
    - satır kaymışsa yakın blok araması yapar
    """
    prepared_code = _prepare_replacement_code(target_item, new_code)
    updated_code = _replace_line_range(source_code, target_item, prepared_code)
    _sanity_check_after_replace(updated_code)
    return updated_code


def _build_backup_path(path_obj: Path) -> Path:
    default_backup = path_obj.with_suffix(path_obj.suffix + ".bak")
    if not default_backup.exists():
        return default_backup

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return path_obj.with_name(f"{path_obj.name}.{ts}.bak")


def _build_temp_write_path(path_obj: Path) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return path_obj.with_name(f".{path_obj.name}.{ts}.tmp")


def _atomic_write_text(path_obj: Path, text: str, encoding: str = "utf-8") -> None:
    """
    Android / Linux tarafında yarım yazma riskini azaltmak için
    geçici dosyaya yazıp ardından replace yapar.
    """
    temp_path = _build_temp_write_path(path_obj)

    try:
        temp_path.write_text(text, encoding=encoding)
        os.replace(str(temp_path), str(path_obj))
    except Exception as exc:
        try:
            if temp_path.exists():
                temp_path.unlink()
        except Exception:
            pass
        raise FunctionReplaceError(f"Güncellenmiş dosya güvenli şekilde yazılamadı: {path_obj}") from exc


def update_function_in_file(
    file_path: str,
    target_item: FunctionItem,
    new_code: str,
    *,
    encoding: str = "utf-8",
    make_backup: bool = True,
) -> str:
    _validate_target_item(target_item)

    raw_path = str(file_path or "").strip()
    if not raw_path:
        raise FunctionReplaceError("Dosya yolu boş.")

    path_obj = Path(raw_path)

    if not path_obj.exists():
        raise FunctionReplaceError(f"Dosya bulunamadı: {path_obj}")
    if not path_obj.is_file():
        raise FunctionReplaceError(f"Geçerli bir dosya değil: {path_obj}")
    if not path_obj.parent.exists():
        raise FunctionReplaceError(f"Hedef klasör bulunamadı: {path_obj.parent}")

    try:
        source_code = path_obj.read_text(encoding=encoding)
    except UnicodeDecodeError as exc:
        raise FunctionReplaceError(
            f"Dosya '{encoding}' ile okunamadı: {path_obj}"
        ) from exc
    except OSError as exc:
        raise FunctionReplaceError(f"Dosya okunamadı: {path_obj}") from exc

    updated_code = update_function_in_code(source_code, target_item, new_code)

    if make_backup:
        backup_path = _build_backup_path(path_obj)
        try:
            shutil.copyfile(path_obj, backup_path)
        except Exception as exc:
            raise FunctionReplaceError(
                f"Yedek dosya oluşturulamadı: {backup_path}"
            ) from exc

    _atomic_write_text(path_obj, updated_code, encoding=encoding)

    return updated_code


def find_item_by_identity(
    items: list[FunctionItem],
    *,
    path: str,
    name: str,
    lineno: int,
    kind: str | None = None,
) -> Optional[FunctionItem]:
    target_path = str(path or "").strip()
    target_name = str(name or "").strip()
    target_kind = str(kind or "").strip()
    target_lineno = int(lineno or 0)

    if not target_path or not target_name or not target_lineno:
        return None

    for item in items:
        if str(item.path).strip() != target_path:
            continue
        if str(item.name).strip() != target_name:
            continue
        if int(item.lineno) != target_lineno:
            continue
        if target_kind and str(item.kind).strip() != target_kind:
            continue
        return item

    for item in items:
        if str(item.path).strip() != target_path:
            continue
        if str(item.name).strip() != target_name:
            continue
        if target_kind and str(item.kind).strip() != target_kind:
            continue
        return item

    for item in items:
        if str(item.name).strip() != target_name:
            continue
        if int(item.lineno) != target_lineno:
            continue
        if target_kind and str(item.kind).strip() != target_kind:
            continue
        return item

    return None