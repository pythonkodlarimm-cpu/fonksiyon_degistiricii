# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/arama/arama.py
"""

from __future__ import annotations


def normalize_query_tokens(value: str) -> list[str]:
    q = str(value or "").strip().lower()
    if not q:
        return []
    return [parca for parca in q.split() if parca]


def item_search_text(item) -> str:
    path = str(getattr(item, "path", "") or "").lower()
    name = str(getattr(item, "name", "") or "").lower()
    kind = str(getattr(item, "kind", "") or "").lower()
    signature = str(getattr(item, "signature", "") or "").lower()
    qualified_name = str(getattr(item, "qualified_name", "") or "").lower()
    parent_name = str(getattr(item, "parent_name", "") or "").lower()
    lineno = str(getattr(item, "lineno", "") or "")
    end_lineno = str(getattr(item, "end_lineno", "") or "")

    alanlar = [
        path,
        name,
        kind,
        signature,
        qualified_name,
        parent_name,
        lineno,
        end_lineno,
        f"{lineno}-{end_lineno}",
        f"satır {lineno}-{end_lineno}",
        f"satir {lineno}-{end_lineno}",
    ]
    return " | ".join(alanlar)


def item_matches_query(item, tokens: list[str]) -> bool:
    if not tokens:
        return True
    haystack = item_search_text(item)
    return all(token in haystack for token in tokens)


def apply_filter(items, value: str):
    tokens = normalize_query_tokens(value)
    if not tokens:
        return list(items or [])

    filtered = []
    for item in list(items or []):
        if item_matches_query(item, tokens):
            filtered.append(item)
    return filtered