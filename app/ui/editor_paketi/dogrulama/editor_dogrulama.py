# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/dogrulama/editor_dogrulama.py

ROL:
- Yeni fonksiyon kodunu normalize etmek
- İlk anlamlı satır ve tam fonksiyon görünümünü kontrol etmek
- AST ile sözdizimi ve yapı doğrulaması yapmak
- Doğrulama sonucunu UI katmanının çevirebileceği anahtarlarla döndürmek

MİMARİ:
- Bu katman kullanıcı dili üretmez
- Kullanıcıya gösterilecek nihai metin UI katmanında çözülmelidir
- Low-level doğrulama bu dosyada sade ve platform bağımsız kalır
- Fail-soft yaklaşımı korunur

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 4
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

import ast


# =========================================================
# NORMALIZE
# =========================================================
def normalize_code_text(text, trim_outer_blank_lines: bool = False) -> str:
    metin = str(text or "")
    metin = metin.replace("\r\n", "\n").replace("\r", "\n").replace("\t", "    ")

    if trim_outer_blank_lines:
        satirlar = metin.split("\n")

        while satirlar and not satirlar[0].strip():
            satirlar.pop(0)

        while satirlar and not satirlar[-1].strip():
            satirlar.pop()

        metin = "\n".join(satirlar)

    return metin


# =========================================================
# ANALIZ
# =========================================================
def first_meaningful_line(text: str) -> str:
    for line in normalize_code_text(text, trim_outer_blank_lines=True).split("\n"):
        satir = line.strip()

        if not satir:
            continue

        if satir.startswith("#"):
            continue

        return satir

    return ""


def looks_like_full_function(text: str) -> bool:
    line = first_meaningful_line(text)

    if line.startswith("@"):
        return True

    return line.startswith("def ") or line.startswith("async def ")


# =========================================================
# AST KONTROL
# =========================================================
def basic_parse_check(text: str) -> None:
    mod = ast.parse(text)

    if not mod.body:
        raise ValueError("validation_error_code_empty")

    if len(mod.body) != 1:
        raise ValueError("validation_error_single_function_required")

    node = mod.body[0]

    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        raise ValueError("validation_error_only_def_allowed")


def extract_line_number(exc) -> int:
    try:
        if getattr(exc, "lineno", None):
            return int(exc.lineno)
    except Exception:
        pass
    return 0


# =========================================================
# ANA VALIDATE
# =========================================================
def validate_new_code(text: str) -> tuple[bool, str, int]:
    yeni = normalize_code_text(text, trim_outer_blank_lines=True)

    if not yeni.strip():
        return False, "validation_error_new_code_empty", 0

    ilk_satir = yeni.split("\n")[0].strip() if yeni else ""

    if not (
        ilk_satir.startswith("def ")
        or ilk_satir.startswith("async def ")
        or ilk_satir.startswith("@")
    ):
        return False, "validation_error_function_must_start_first_line", 1

    if not looks_like_full_function(yeni):
        return False, "validation_error_first_meaningful_line_must_be_def", 1

    try:
        basic_parse_check(yeni)

    except SyntaxError as exc:
        satir = int(getattr(exc, "lineno", 0) or 0)
        sutun = int(getattr(exc, "offset", 0) or 0)
        mesaj = str(getattr(exc, "msg", "") or "").strip() or "syntax error"
        return (
            False,
            f"validation_error_syntax|line={satir}|column={sutun}|message={mesaj}",
            extract_line_number(exc),
        )

    except ValueError as exc:
        return False, str(exc), 1

    except Exception as exc:
        return False, str(exc), extract_line_number(exc)

    return True, "", 0
