# -*- coding: utf-8 -*-
"""
DOSYA: app/core/parca_degistirme/degistirici.py

ROL:
- Kaynak kod içindeki belirli bir metin parçasını güvenli biçimde değiştirir
- Parça bazlı replace işlemini merkezileştirir
- Bellek içi ve dosya üstü çalışma desteği sağlar
- Final syntax kontrolü yapar
- Motor bazlı yedekleme entegrasyonu içerir

MİMARİ:
- Saf Python çalışır
- String tabanlı replace yapar
- Değiştirilecek parça boş olamaz
- Yeni parça boş olabilir
- first / all / exact_count modlarını destekler
- full_line_* ve full_block_* modları ile tam satır / tam blok eşleşme sağlar
- semantic_block_* modları ile indent-normalize blok eşleşmesi sağlar
- Dosya yazımı atomik yapılır
- Yedekler ortak yedekleme altyapısı üzerinden motor klasörüne yazılır

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Pydroid3 / masaüstü / test ortamlarında aynı davranır

SURUM: 4
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

import ast
import os
import shutil
import textwrap
from pathlib import Path
from typing import Callable, Final


# =========================================================
# MODES
# =========================================================
MODE_FIRST: Final[str] = "first"
MODE_ALL: Final[str] = "all"
MODE_EXACT_COUNT: Final[str] = "exact_count"

MODE_FULL_LINE_FIRST: Final[str] = "full_line_first"
MODE_FULL_LINE_ALL: Final[str] = "full_line_all"
MODE_FULL_LINE_EXACT_COUNT: Final[str] = "full_line_exact_count"

MODE_FULL_BLOCK_FIRST: Final[str] = "full_block_first"
MODE_FULL_BLOCK_ALL: Final[str] = "full_block_all"
MODE_FULL_BLOCK_EXACT_COUNT: Final[str] = "full_block_exact_count"

MODE_SEMANTIC_BLOCK_FIRST: Final[str] = "semantic_block_first"
MODE_SEMANTIC_BLOCK_ALL: Final[str] = "semantic_block_all"
MODE_SEMANTIC_BLOCK_EXACT_COUNT: Final[str] = "semantic_block_exact_count"

ALLOWED_MODES: Final[frozenset[str]] = frozenset(
    {
        MODE_FIRST,
        MODE_ALL,
        MODE_EXACT_COUNT,
        MODE_FULL_LINE_FIRST,
        MODE_FULL_LINE_ALL,
        MODE_FULL_LINE_EXACT_COUNT,
        MODE_FULL_BLOCK_FIRST,
        MODE_FULL_BLOCK_ALL,
        MODE_FULL_BLOCK_EXACT_COUNT,
        MODE_SEMANTIC_BLOCK_FIRST,
        MODE_SEMANTIC_BLOCK_ALL,
        MODE_SEMANTIC_BLOCK_EXACT_COUNT,
    }
)


# =========================================================
# ERROR
# =========================================================
class ParcaDegistirmeHatasi(ValueError):
    """
    Parça değiştirme sırasında oluşan kontrollü hata.
    """


# =========================================================
# LAZY BACKUP CACHE
# =========================================================
_backup_dosya_yolu_uret_fn: Callable[..., Path] | None = None


def _backup_yolu_uretici() -> Callable[..., Path]:
    global _backup_dosya_yolu_uret_fn

    fn = _backup_dosya_yolu_uret_fn
    if fn is None:
        from app.core.yedekleme.yollar import backup_dosya_yolu_uret

        fn = backup_dosya_yolu_uret
        _backup_dosya_yolu_uret_fn = fn

    return fn


# =========================================================
# NORMALIZE
# =========================================================
def _normalize_text(text: str) -> str:
    return str(text or "").replace("\r\n", "\n").replace("\r", "\n")


def _strip_only_edge_newlines(text: str) -> str:
    return _normalize_text(text).strip("\n")


# =========================================================
# VALIDATION
# =========================================================
def _validate_mode(mode: str) -> str:
    normalized = str(mode or "").strip().lower()

    if normalized not in ALLOWED_MODES:
        raise ParcaDegistirmeHatasi(
            f"Geçersiz mode: {mode!r}. Desteklenen modlar: {sorted(ALLOWED_MODES)}"
        )

    return normalized


def _validate_old_piece(old_piece: str) -> str:
    normalized = _normalize_text(old_piece)

    if not normalized:
        raise ParcaDegistirmeHatasi("Değiştirilecek parça boş olamaz.")

    return normalized


# =========================================================
# BASIC REPLACE
# =========================================================
def _count_occurrences(source_code: str, old_piece: str) -> int:
    return _normalize_text(source_code).count(old_piece)


def _replace_first(
    source_code: str,
    old_piece: str,
    new_piece: str,
) -> tuple[str, int]:
    count = _count_occurrences(source_code, old_piece)

    if count <= 0:
        raise ParcaDegistirmeHatasi(
            "Değiştirilecek parça kaynak kod içinde bulunamadı."
        )

    updated = source_code.replace(old_piece, new_piece, 1)
    return updated, 1


def _replace_all(
    source_code: str,
    old_piece: str,
    new_piece: str,
) -> tuple[str, int]:
    count = _count_occurrences(source_code, old_piece)

    if count <= 0:
        raise ParcaDegistirmeHatasi(
            "Değiştirilecek parça kaynak kod içinde bulunamadı."
        )

    updated = source_code.replace(old_piece, new_piece)
    return updated, count


def _replace_exact_count(
    source_code: str,
    old_piece: str,
    new_piece: str,
    expected_count: int,
) -> tuple[str, int]:
    if expected_count <= 0:
        raise ParcaDegistirmeHatasi("expected_count 1 veya daha büyük olmalıdır.")

    count = _count_occurrences(source_code, old_piece)

    if count != expected_count:
        raise ParcaDegistirmeHatasi(
            f"Eşleşme sayısı beklenen değeri karşılamadı. "
            f"Beklenen={expected_count}, Bulunan={count}"
        )

    updated = source_code.replace(old_piece, new_piece)
    return updated, count


# =========================================================
# FULL LINE MODES
# =========================================================
def _build_full_line_piece(piece: str) -> str:
    normalized = _strip_only_edge_newlines(piece)

    if not normalized:
        raise ParcaDegistirmeHatasi("Tam satır eşleşmesi için parça boş olamaz.")

    if "\n" in normalized:
        raise ParcaDegistirmeHatasi(
            "Tam satır modu yalnızca tek satırlı parça ile kullanılabilir."
        )

    return normalized + "\n"


def _replace_full_line_first(
    source_code: str,
    old_piece: str,
    new_piece: str,
) -> tuple[str, int]:
    old_line = _build_full_line_piece(old_piece)
    new_line = _strip_only_edge_newlines(new_piece) + "\n"
    return _replace_first(source_code, old_line, new_line)


def _replace_full_line_all(
    source_code: str,
    old_piece: str,
    new_piece: str,
) -> tuple[str, int]:
    old_line = _build_full_line_piece(old_piece)
    new_line = _strip_only_edge_newlines(new_piece) + "\n"
    return _replace_all(source_code, old_line, new_line)


def _replace_full_line_exact_count(
    source_code: str,
    old_piece: str,
    new_piece: str,
    expected_count: int,
) -> tuple[str, int]:
    old_line = _build_full_line_piece(old_piece)
    new_line = _strip_only_edge_newlines(new_piece) + "\n"
    return _replace_exact_count(source_code, old_line, new_line, expected_count)


# =========================================================
# FULL BLOCK MODES
# =========================================================
def _build_full_block_piece(piece: str) -> str:
    normalized = _strip_only_edge_newlines(piece)

    if not normalized:
        raise ParcaDegistirmeHatasi("Tam blok eşleşmesi için parça boş olamaz.")

    return normalized


def _replace_full_block_first(
    source_code: str,
    old_piece: str,
    new_piece: str,
) -> tuple[str, int]:
    old_block = _build_full_block_piece(old_piece)
    new_block = _strip_only_edge_newlines(new_piece)
    return _replace_first(source_code, old_block, new_block)


def _replace_full_block_all(
    source_code: str,
    old_piece: str,
    new_piece: str,
) -> tuple[str, int]:
    old_block = _build_full_block_piece(old_piece)
    new_block = _strip_only_edge_newlines(new_piece)
    return _replace_all(source_code, old_block, new_block)


def _replace_full_block_exact_count(
    source_code: str,
    old_piece: str,
    new_piece: str,
    expected_count: int,
) -> tuple[str, int]:
    old_block = _build_full_block_piece(old_piece)
    new_block = _strip_only_edge_newlines(new_piece)
    return _replace_exact_count(source_code, old_block, new_block, expected_count)


# =========================================================
# SEMANTIC BLOCK MODES
# =========================================================
def _semantic_normalize_block(piece: str) -> str:
    normalized = _normalize_text(piece)
    normalized = normalized.strip("\n")
    normalized = textwrap.dedent(normalized)
    normalized = normalized.strip("\n")

    if not normalized.strip():
        raise ParcaDegistirmeHatasi(
            "Semantic blok eşleşmesi için parça boş olamaz."
        )

    return normalized


def _build_semantic_source_variants(
    source_code: str,
) -> list[tuple[int, int, str]]:
    """
    Kaynak koddan semantic blok araması için aday varyantlar üretir.

    Dönüş:
    - (başlangıç_offset, bitiş_offset, normalize_blok)

    Her aday, ardışık satır bloklarından oluşur ve soldan ortak girinti
    normalize edilerek karşılaştırmaya hazır hale getirilir.
    """
    normalized_source = _normalize_text(source_code)
    lines = normalized_source.splitlines(keepends=True)

    variants: list[tuple[int, int, str]] = []
    line_offsets: list[int] = []

    cursor = 0
    for line in lines:
        line_offsets.append(cursor)
        cursor += len(line)

    total = len(lines)

    for start in range(total):
        for end in range(start + 1, total + 1):
            block = "".join(lines[start:end]).strip("\n")
            if not block.strip():
                continue

            normalized_block = textwrap.dedent(block).strip("\n")
            if not normalized_block.strip():
                continue

            start_offset = line_offsets[start]
            end_offset = cursor if end == total else line_offsets[end]
            variants.append((start_offset, end_offset, normalized_block))

    return variants


def _find_semantic_matches(
    source_code: str,
    old_piece: str,
) -> list[tuple[int, int]]:
    target = _semantic_normalize_block(old_piece)
    variants = _build_semantic_source_variants(source_code)

    matches: list[tuple[int, int]] = []

    for start_offset, end_offset, normalized_block in variants:
        if normalized_block == target:
            matches.append((start_offset, end_offset))

    return matches


def _replace_semantic_matches(
    source_code: str,
    old_piece: str,
    new_piece: str,
    *,
    mode: str,
    expected_count: int,
) -> tuple[str, int]:
    matches = _find_semantic_matches(source_code, old_piece)

    if not matches:
        raise ParcaDegistirmeHatasi(
            "Semantic blok kaynak kod içinde bulunamadı."
        )

    normalized_new = _semantic_normalize_block(new_piece)

    if mode == MODE_SEMANTIC_BLOCK_FIRST:
        selected = [matches[0]]
    elif mode == MODE_SEMANTIC_BLOCK_ALL:
        selected = matches
    else:
        if expected_count <= 0:
            raise ParcaDegistirmeHatasi(
                "expected_count 1 veya daha büyük olmalıdır."
            )

        if len(matches) != expected_count:
            raise ParcaDegistirmeHatasi(
                f"Eşleşme sayısı beklenen değeri karşılamadı. "
                f"Beklenen={expected_count}, Bulunan={len(matches)}"
            )

        selected = matches

    updated = source_code

    for start_offset, end_offset in reversed(selected):
        original_block = updated[start_offset:end_offset]
        original_lines = original_block.splitlines(keepends=True)

        first_non_empty = ""
        for line in original_lines:
            if line.strip():
                first_non_empty = line
                break

        indent_prefix = first_non_empty[
            : len(first_non_empty) - len(first_non_empty.lstrip(" "))
        ]

        new_lines: list[str] = []
        for line in normalized_new.splitlines():
            if line.strip():
                new_lines.append(indent_prefix + line)
            else:
                new_lines.append("")

        replacement = "\n".join(new_lines)

        if original_block.endswith("\n"):
            replacement += "\n"

        updated = updated[:start_offset] + replacement + updated[end_offset:]

    return updated, len(selected)


# =========================================================
# SYNTAX
# =========================================================
def _syntax_check_if_python(source_code: str, strict_python: bool) -> None:
    if not strict_python:
        return

    try:
        ast.parse(source_code)
    except SyntaxError as exc:
        raise ParcaDegistirmeHatasi(
            "Değişiklik sonrası Python sözdizimi bozuldu."
        ) from exc


# =========================================================
# CORE API
# =========================================================
def replace_piece_in_code(
    source_code: str,
    old_piece: str,
    new_piece: str,
    *,
    mode: str = MODE_FIRST,
    expected_count: int = 1,
    strict_python: bool = True,
) -> tuple[str, int]:
    """
    Kaynak kod içindeki bir metin parçasını değiştirir.

    Args:
        source_code:
            Üzerinde işlem yapılacak kaynak metin.
        old_piece:
            Değiştirilecek mevcut parça. Boş olamaz.
        new_piece:
            Yeni parça. Boş olabilir.
        mode:
            - first
            - all
            - exact_count
            - full_line_first
            - full_line_all
            - full_line_exact_count
            - full_block_first
            - full_block_all
            - full_block_exact_count
            - semantic_block_first
            - semantic_block_all
            - semantic_block_exact_count
        expected_count:
            Sadece *_exact_count modları için kullanılır.
        strict_python:
            True ise final çıktı ast.parse ile doğrulanır.

    Returns:
        (güncellenmiş_kod, değiştirilen_adet)
    """
    normalized_source = _normalize_text(source_code)
    normalized_old = _validate_old_piece(old_piece)
    normalized_new = _normalize_text(new_piece)
    normalized_mode = _validate_mode(mode)

    if normalized_mode == MODE_FIRST:
        updated, replaced_count = _replace_first(
            normalized_source,
            normalized_old,
            normalized_new,
        )
    elif normalized_mode == MODE_ALL:
        updated, replaced_count = _replace_all(
            normalized_source,
            normalized_old,
            normalized_new,
        )
    elif normalized_mode == MODE_EXACT_COUNT:
        updated, replaced_count = _replace_exact_count(
            normalized_source,
            normalized_old,
            normalized_new,
            int(expected_count or 0),
        )
    elif normalized_mode == MODE_FULL_LINE_FIRST:
        updated, replaced_count = _replace_full_line_first(
            normalized_source,
            normalized_old,
            normalized_new,
        )
    elif normalized_mode == MODE_FULL_LINE_ALL:
        updated, replaced_count = _replace_full_line_all(
            normalized_source,
            normalized_old,
            normalized_new,
        )
    elif normalized_mode == MODE_FULL_LINE_EXACT_COUNT:
        updated, replaced_count = _replace_full_line_exact_count(
            normalized_source,
            normalized_old,
            normalized_new,
            int(expected_count or 0),
        )
    elif normalized_mode == MODE_FULL_BLOCK_FIRST:
        updated, replaced_count = _replace_full_block_first(
            normalized_source,
            normalized_old,
            normalized_new,
        )
    elif normalized_mode == MODE_FULL_BLOCK_ALL:
        updated, replaced_count = _replace_full_block_all(
            normalized_source,
            normalized_old,
            normalized_new,
        )
    elif normalized_mode == MODE_FULL_BLOCK_EXACT_COUNT:
        updated, replaced_count = _replace_full_block_exact_count(
            normalized_source,
            normalized_old,
            normalized_new,
            int(expected_count or 0),
        )
    else:
        updated, replaced_count = _replace_semantic_matches(
            normalized_source,
            normalized_old,
            normalized_new,
            mode=normalized_mode,
            expected_count=int(expected_count or 0),
        )

    _syntax_check_if_python(updated, strict_python)
    return updated, replaced_count


# =========================================================
# FILE HELPERS
# =========================================================
def _build_backup_path(path_obj: Path) -> Path:
    """
    Motor bazlı Android uyumlu backup dosya yolu üretir.
    """
    return _backup_yolu_uretici()(
        motor_adi="parca_degistirme",
        kaynak_dosya_adi=path_obj.name,
        uzanti=".bak",
    )


def _build_temp_write_path(path_obj: Path) -> Path:
    """
    Atomik yazma için geçici dosya yolu üretir.
    """
    return path_obj.with_suffix(path_obj.suffix + ".tmp")


def _safe_remove(path_obj: Path) -> None:
    try:
        if path_obj.exists():
            path_obj.unlink()
    except Exception:
        pass


def _atomic_write_text(
    path_obj: Path,
    text: str,
    encoding: str = "utf-8",
) -> None:
    temp_path = _build_temp_write_path(path_obj)

    try:
        temp_path.write_text(text, encoding=encoding)
        os.replace(str(temp_path), str(path_obj))
    except Exception as exc:
        _safe_remove(temp_path)
        raise ParcaDegistirmeHatasi(
            f"Dosya güvenli şekilde yazılamadı: {path_obj}"
        ) from exc


# =========================================================
# FILE API
# =========================================================
def replace_piece_in_file(
    file_path: str,
    old_piece: str,
    new_piece: str,
    *,
    mode: str = MODE_FIRST,
    expected_count: int = 1,
    strict_python: bool = True,
    encoding: str = "utf-8",
    make_backup: bool = True,
) -> tuple[str, int]:
    """
    Dosya içindeki bir metin parçasını değiştirir ve dosyaya yazar.

    Returns:
        (güncellenmiş_kod, değiştirilen_adet)
    """
    raw_path = str(file_path or "").strip()

    if not raw_path:
        raise ParcaDegistirmeHatasi("Dosya yolu boş.")

    path_obj = Path(raw_path)

    if not path_obj.exists():
        raise ParcaDegistirmeHatasi(f"Dosya bulunamadı: {path_obj}")

    if not path_obj.is_file():
        raise ParcaDegistirmeHatasi(f"Geçerli bir dosya değil: {path_obj}")

    try:
        source_code = path_obj.read_text(encoding=encoding)
    except UnicodeDecodeError as exc:
        raise ParcaDegistirmeHatasi(
            f"Dosya '{encoding}' ile okunamadı: {path_obj}"
        ) from exc
    except OSError as exc:
        raise ParcaDegistirmeHatasi(
            f"Dosya okunamadı: {path_obj}"
        ) from exc

    updated_code, replaced_count = replace_piece_in_code(
        source_code=source_code,
        old_piece=old_piece,
        new_piece=new_piece,
        mode=mode,
        expected_count=expected_count,
        strict_python=strict_python,
    )

    if make_backup:
        backup_path = _build_backup_path(path_obj)
        try:
            shutil.copyfile(path_obj, backup_path)
        except Exception as exc:
            raise ParcaDegistirmeHatasi(
                f"Yedek dosya oluşturulamadı: {backup_path}"
            ) from exc

    _atomic_write_text(path_obj, updated_code, encoding=encoding)
    return updated_code, replaced_count