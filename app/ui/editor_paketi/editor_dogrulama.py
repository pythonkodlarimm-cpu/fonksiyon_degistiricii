# -*- coding: utf-8 -*-
from __future__ import annotations

import ast


def normalize_code_text(text, trim_outer_blank_lines=False) -> str:
    metin = str(text or "").replace("\r\n", "\n").replace("\r", "\n").replace("\t", "    ")

    if trim_outer_blank_lines:
        satirlar = metin.split("\n")
        while satirlar and not satirlar[0].strip():
            satirlar.pop(0)
        while satirlar and not satirlar[-1].strip():
            satirlar.pop()
        metin = "\n".join(satirlar)

    return metin


def first_meaningful_line(text: str) -> str:
    for line in normalize_code_text(text, trim_outer_blank_lines=True).split("\n"):
        s = line.strip()
        if s and not s.startswith("#"):
            return s
    return ""


def looks_like_full_function(text: str) -> bool:
    line = first_meaningful_line(text)
    return line.startswith("def ") or line.startswith("async def ")


def basic_parse_check(text: str) -> None:
    mod = ast.parse(text)
    if len(mod.body) != 1:
        raise ValueError("Yeni kod tam olarak tek bir fonksiyon içermelidir.")
    if not isinstance(mod.body[0], (ast.FunctionDef, ast.AsyncFunctionDef)):
        raise ValueError("Yeni kod yalnızca tek bir def veya async def içermelidir.")


def extract_line_number(exc) -> int:
    try:
        if getattr(exc, "lineno", None):
            return int(exc.lineno)
    except Exception:
        pass
    return 0


def validate_new_code(text: str) -> tuple[bool, str, int]:
    yeni = normalize_code_text(text, trim_outer_blank_lines=True)

    if not yeni.strip():
        return False, "Yeni kod alanı boş bırakılamaz.", 0

    ilk_satir = yeni.split("\n")[0].strip() if yeni else ""
    if not (ilk_satir.startswith("def ") or ilk_satir.startswith("async def ")):
        return False, "Fonksiyon tanımı 1. satırda başlamalıdır.", 1

    if not looks_like_full_function(yeni):
        return False, "Kodun ilk anlamlı satırı 'def' veya 'async def' olmalıdır.", 1

    try:
        basic_parse_check(yeni)
    except SyntaxError as exc:
        return (
            False,
            f"Sözdizimi hatası: satır {exc.lineno}, sütun {exc.offset} -> {exc.msg}",
            extract_line_number(exc),
        )
    except ValueError as exc:
        return False, str(exc), 1
    except Exception as exc:
        return False, str(exc), extract_line_number(exc)

    return True, "", 0