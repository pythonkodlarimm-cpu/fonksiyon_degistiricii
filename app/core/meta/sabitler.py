# -*- coding: utf-8 -*-
"""
DOSYA: app/core/meta/sabitler.py

ROL:
- Uygulama genel sabitlerini içerir
- Android ortamında gerçek APK/AAB kurulu sürüm bilgisini runtime'da çözer
- Android dışı ortamlarda güvenli fallback sağlar
- Uygulama etiketi, meta bilgisi ve sürüm yardımcılarını tek yerde toplar

MİMARİ:
- Sabitler + runtime çözümleme birlikte çalışır
- Android'de PackageManager üzerinden gerçek versionName / versionCode okunur
- Android dışı ortamlarda fallback değerler kullanılır
- Üst katman doğrudan bu dosyayı değil meta yöneticisini kullanmalıdır
- Fail-soft davranır
- Deterministik + güvenli fallback yapısı korunur

ANDROID NOTLARI:
- get_apk_surum_adi() -> kurulu uygulamanın gerçek versionName bilgisini döndürür
- get_apk_surum_kodu() -> kurulu uygulamanın gerçek versionCode bilgisini döndürür
- Play Store / release APK / test APK hangi sürüm kuruluysa o gösterilir
- Pydroid3 / masaüstü ortamlarında fallback + [DEV] etiketi kullanılır

BAĞIMLILIKLAR:
- kivy.utils.platform
- Android ortamında opsiyonel olarak pyjnius

API UYUMLULUK:
- Platform bağımsız fallback içerir
- Android API 35 ile uyumludur

SURUM: 4
TARIH: 2026-03-29
IMZA: FY.
"""

from __future__ import annotations

from typing import Dict, Tuple

from kivy.utils import platform

# =========================================================
# TEMEL KIMLIK
# =========================================================
UYGULAMA_ADI: str = "Fonksiyon Değiştirici"
PAKET_ADI: str = "org.fy.fonksiyon_degistirici"

# =========================================================
# FALLBACK SURUM
# =========================================================
# Not:
# - Android dışında veya runtime çözümleme başarısız olursa bunlar kullanılır.
# - CI/CD tarafında isterse bu alanlar yine güncellenebilir.
SURUM_ADI: str = "0.1.0"
SURUM_KODU: int = 1
BUILD_NUMARASI: int = 1

# =========================================================
# DIGER META
# =========================================================
TARIH: str = "2026-03-29"
IMZA: str = "FY."

ACIKLAMA: str = (
    "Python dosyalarındaki fonksiyonları ve nested function'ları "
    "arayüz üzerinden seçip güncellemek için geliştirilen uygulama."
)


# =========================================================
# INTERNAL YARDIMCILAR
# =========================================================
def _safe_str(value, default: str = "") -> str:
    """
    Değeri güvenli biçimde str'e çevirir.
    """
    try:
        metin = str(value)
        return metin if metin is not None else default
    except Exception:
        return default


def _safe_int(value, default: int = 0) -> int:
    """
    Değeri güvenli biçimde int'e çevirir.
    """
    try:
        return int(value)
    except Exception:
        return default


def _android_package_info() -> Tuple[str, int] | None:
    """
    Android ortamında kurulu uygulamanın gerçek package bilgisini döndürür.

    Returns:
        (version_name, version_code) veya None
    """
    if platform != "android":
        return None

    try:
        from jnius import autoclass

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        activity = PythonActivity.mActivity

        if activity is None:
            return None

        package_manager = activity.getPackageManager()
        package_name = activity.getPackageName()
        package_info = package_manager.getPackageInfo(package_name, 0)

        version_name = _safe_str(getattr(package_info, "versionName", ""), "")
        version_code = 0

        try:
            version_code = _safe_int(package_info.getLongVersionCode(), 0)
        except Exception:
            try:
                version_code = _safe_int(getattr(package_info, "versionCode", 0), 0)
            except Exception:
                version_code = 0

        if not version_name:
            return None

        return version_name, version_code

    except Exception:
        return None


# =========================================================
# FORMATLI VERILER
# =========================================================
def get_tam_surum() -> str:
    """
    Fallback / legacy tam sürüm stringi.
    """
    return f"{SURUM_ADI} ({BUILD_NUMARASI})"


def get_apk_surum_kodu() -> int:
    """
    Android'de gerçek versionCode, diğer ortamlarda fallback sürüm kodu.
    """
    info = _android_package_info()
    if info is not None:
        return _safe_int(info[1], SURUM_KODU)

    return SURUM_KODU


def get_apk_surum_adi() -> str:
    """
    Android'de gerçek versionName, diğer ortamlarda fallback sürüm adı.

    Android dışı ortamda [DEV] etiketi eklenir.
    """
    info = _android_package_info()
    if info is not None:
        return _safe_str(info[0], SURUM_ADI)

    if platform == "android":
        return SURUM_ADI

    return f"{SURUM_ADI} [DEV]"


def get_apk_tam_surum() -> str:
    """
    Gerçek APK/AAB tam sürüm stringi.
    """
    return f"{get_apk_surum_adi()} ({get_apk_surum_kodu()})"


def get_uygulama_etiketi() -> str:
    """
    UI / toolbar / about ekranı için kısa etiket.

    Örnek:
    - FY. v0.1.449
    - FY. v0.1.0 [DEV]
    """
    return f"{IMZA} v{get_apk_surum_adi()}"


def get_meta_bilgisi() -> Dict[str, str | int]:
    """
    Toplu metadata çıktısı.
    """
    return {
        "uygulama_adi": UYGULAMA_ADI,
        "paket_adi": PAKET_ADI,
        "surum_adi": SURUM_ADI,
        "surum_kodu": SURUM_KODU,
        "build": BUILD_NUMARASI,
        "tarih": TARIH,
        "imza": IMZA,
        "aciklama": ACIKLAMA,
        "tam_surum": get_tam_surum(),
        "apk_surum_adi": get_apk_surum_adi(),
        "apk_surum_kodu": get_apk_surum_kodu(),
        "apk_tam_surum": get_apk_tam_surum(),
        "uygulama_etiketi": get_uygulama_etiketi(),
    }


def get_apk_surum_bilgisi() -> Dict[str, str | int]:
    """
    APK/AAB sürüm bilgisini normalize edilmiş formatta döndürür.
    """
    version_name = get_apk_surum_adi()
    version_code = get_apk_surum_kodu()

    return {
        "version_name": version_name,
        "version_code": version_code,
        "full": f"{version_name} ({version_code})",
        "label": get_uygulama_etiketi(),
}
