# -*- coding: utf-8 -*-
"""
DOSYA: app/services/sistem/dil_servisi.py

ROL:
- Uygulama içi çok dilli metin altyapısını merkezi olarak yönetmek
- Aktif dili ayar_servisi üzerinden okuyup uygulama metinlerini üretmek
- Desteklenen dil listesini dış katmanlara sunmak
- Eksik çeviri durumunda güvenli fallback zinciri uygulamak

MİMARİ:
- Aktif dil bilgisi ayar_servisi içindeki language alanından okunur
- Tüm dil meta verileri ve uygulama içi metin anahtarları bu dosyada tutulur
- UI katmanı sabit metin yazmak yerine bu servis üzerinden metin alır
- Çeviri eksikse önce İngilizceye, sonra Türkçeye, sonra anahtar adına fallback yapılır
- Büyük ölçekli dil desteğine uygun genişletilebilir sözlük yapısı kullanılır
- ayar_servisi ile desteklenen dil kodları senkron tutulur

FALLBACK STRATEJİSİ:
- secili_dil -> en -> tr -> anahtar
- Böylece eksik çeviri uygulamayı bozmaz
- Yeni dil eklenirken sadece eksik anahtarlar sonradan doldurulabilir

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 uyumludur
- Android ve masaüstü ortamlarda güvenli çalışır
- UI yenileme akışları için okunabilir ve deterministik sonuç döndürür

GENISLEME NOTLARI:
- Şimdilik çekirdek metinler az sayıda tutulur
- Ancak dil kayıt yapısı Play Store'da yaygın kullanılan geniş dil ağını destekleyecek
- İleride yeni dil eklemek için:
  1) DIL_BILGILERI içine dil meta verisi eklenir
  2) METINLER içine ilgili dil sözlüğü eklenir
  3) Eksik anahtarlar fallback ile güvenli şekilde çalışmaya devam eder

SURUM: 2
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

from app.services.sistem.ayar_servisi import (
    DEFAULT_LANGUAGE,
    get_language,
    supported_languages,
)


# =========================================================
# DIL META BILGILERI
# =========================================================
DIL_BILGILERI: dict[str, dict[str, object]] = {
    "tr": {"ad": "Türkçe", "yerel_ad": "Türkçe", "aktif": True},
    "en": {"ad": "İngilizce", "yerel_ad": "English", "aktif": True},
    "de": {"ad": "Almanca", "yerel_ad": "Deutsch", "aktif": True},
    "fr": {"ad": "Fransızca", "yerel_ad": "Français", "aktif": False},
    "es": {"ad": "İspanyolca", "yerel_ad": "Español", "aktif": False},
    "it": {"ad": "İtalyanca", "yerel_ad": "Italiano", "aktif": False},
    "pt": {"ad": "Portekizce", "yerel_ad": "Português", "aktif": False},
    "pt-br": {
        "ad": "Portekizce (Brezilya)",
        "yerel_ad": "Português (Brasil)",
        "aktif": False,
    },
    "nl": {"ad": "Felemenkçe", "yerel_ad": "Nederlands", "aktif": False},
    "ru": {"ad": "Rusça", "yerel_ad": "Русский", "aktif": False},
    "uk": {"ad": "Ukraynaca", "yerel_ad": "Українська", "aktif": False},
    "pl": {"ad": "Lehçe", "yerel_ad": "Polski", "aktif": False},
    "cs": {"ad": "Çekçe", "yerel_ad": "Čeština", "aktif": False},
    "sk": {"ad": "Slovakça", "yerel_ad": "Slovenčina", "aktif": False},
    "sl": {"ad": "Slovence", "yerel_ad": "Slovenščina", "aktif": False},
    "hr": {"ad": "Hırvatça", "yerel_ad": "Hrvatski", "aktif": False},
    "sr": {"ad": "Sırpça", "yerel_ad": "Српски", "aktif": False},
    "bg": {"ad": "Bulgarca", "yerel_ad": "Български", "aktif": False},
    "ro": {"ad": "Romence", "yerel_ad": "Română", "aktif": False},
    "hu": {"ad": "Macarca", "yerel_ad": "Magyar", "aktif": False},
    "el": {"ad": "Yunanca", "yerel_ad": "Ελληνικά", "aktif": False},
    "da": {"ad": "Danca", "yerel_ad": "Dansk", "aktif": False},
    "sv": {"ad": "İsveççe", "yerel_ad": "Svenska", "aktif": False},
    "no": {"ad": "Norveççe", "yerel_ad": "Norsk", "aktif": False},
    "fi": {"ad": "Fince", "yerel_ad": "Suomi", "aktif": False},
    "et": {"ad": "Estonca", "yerel_ad": "Eesti", "aktif": False},
    "lv": {"ad": "Letonca", "yerel_ad": "Latviešu", "aktif": False},
    "lt": {"ad": "Litvanca", "yerel_ad": "Lietuvių", "aktif": False},
    "ga": {"ad": "İrlandaca", "yerel_ad": "Gaeilge", "aktif": False},
    "mt": {"ad": "Maltaca", "yerel_ad": "Malti", "aktif": False},
    "cy": {"ad": "Galce", "yerel_ad": "Cymraeg", "aktif": False},
    "ca": {"ad": "Katalanca", "yerel_ad": "Català", "aktif": False},
    "eu": {"ad": "Baskça", "yerel_ad": "Euskara", "aktif": False},
    "gl": {"ad": "Galiçyaca", "yerel_ad": "Galego", "aktif": False},
    "af": {"ad": "Afrikaanca", "yerel_ad": "Afrikaans", "aktif": False},
    "sw": {"ad": "Svahili", "yerel_ad": "Kiswahili", "aktif": False},
    "zu": {"ad": "Zulu", "yerel_ad": "isiZulu", "aktif": False},
    "xh": {"ad": "Xhosa", "yerel_ad": "isiXhosa", "aktif": False},
    "am": {"ad": "Amharca", "yerel_ad": "አማርኛ", "aktif": False},
    "ar": {"ad": "Arapça", "yerel_ad": "العربية", "aktif": False},
    "fa": {"ad": "Farsça", "yerel_ad": "فارسی", "aktif": False},
    "ur": {"ad": "Urduca", "yerel_ad": "اردو", "aktif": False},
    "he": {"ad": "İbranice", "yerel_ad": "עברית", "aktif": False},
    "hi": {"ad": "Hintçe", "yerel_ad": "हिन्दी", "aktif": False},
    "bn": {"ad": "Bengalce", "yerel_ad": "বাংলা", "aktif": False},
    "ta": {"ad": "Tamilce", "yerel_ad": "தமிழ்", "aktif": False},
    "te": {"ad": "Telugu", "yerel_ad": "తెలుగు", "aktif": False},
    "ml": {"ad": "Malayalam", "yerel_ad": "മലയാളം", "aktif": False},
    "kn": {"ad": "Kannada", "yerel_ad": "ಕನ್ನಡ", "aktif": False},
    "gu": {"ad": "Gujarati", "yerel_ad": "ગુજરાતી", "aktif": False},
    "mr": {"ad": "Marathi", "yerel_ad": "मराठी", "aktif": False},
    "pa": {"ad": "Pencapça", "yerel_ad": "ਪੰਜਾਬੀ", "aktif": False},
    "or": {"ad": "Odia", "yerel_ad": "ଓଡ଼ିଆ", "aktif": False},
    "as": {"ad": "Assamca", "yerel_ad": "অসমীয়া", "aktif": False},
    "ne": {"ad": "Nepalce", "yerel_ad": "नेपाली", "aktif": False},
    "si": {"ad": "Sinhalaca", "yerel_ad": "සිංහල", "aktif": False},
    "my": {"ad": "Burmaca", "yerel_ad": "မြန်မာ", "aktif": False},
    "th": {"ad": "Tayca", "yerel_ad": "ไทย", "aktif": False},
    "vi": {"ad": "Vietnamca", "yerel_ad": "Tiếng Việt", "aktif": False},
    "id": {"ad": "Endonezce", "yerel_ad": "Bahasa Indonesia", "aktif": False},
    "ms": {"ad": "Malayca", "yerel_ad": "Bahasa Melayu", "aktif": False},
    "tl": {"ad": "Tagalog", "yerel_ad": "Tagalog", "aktif": False},
    "zh": {"ad": "Çince", "yerel_ad": "中文", "aktif": False},
    "zh-cn": {
        "ad": "Çince (Basitleştirilmiş)",
        "yerel_ad": "简体中文",
        "aktif": False,
    },
    "zh-tw": {
        "ad": "Çince (Geleneksel)",
        "yerel_ad": "繁體中文",
        "aktif": False,
    },
    "ja": {"ad": "Japonca", "yerel_ad": "日本語", "aktif": False},
    "ko": {"ad": "Korece", "yerel_ad": "한국어", "aktif": False},
}


# =========================================================
# METIN SOZLUKLERI
# =========================================================
METINLER: dict[str, dict[str, str]] = {
    "tr": {
        "app_ready": "Hazır.",
        "settings": "Ayarlar",
        "language": "Dil",
        "select_language": "Dil Seç",
        "language_saved": "Dil kaydedildi.",
        "language_updated": "Dil güncellendi.",
        "file_not_selected": "Dosya seçilmedi",
        "file_info_placeholder": "Seçilen belge bilgisi burada görünür.",
        "file_waiting": "Belge seçmeniz bekleniyor.",
        "file_selected_auto_scan": "Belge seçildi • Tarama otomatik başlatılır.",
        "select_file": "Dosya Seç",
        "test": "Test",
        "scan_completed": "Tarama tamamlandı.",
        "update": "Güncelle",
        "new_version_available": "Yeni sürüm mevcut.",
        "open_list": "Listeyi Aç",
        "session_restored": "Oturum geri yüklendi.",
        "previous_session_restored": "Önceki oturum geri yüklendi.",
        "all_files_access_open": "Tüm dosya erişimi açık.",
        "all_files_access_closed": "Tüm dosya erişimi kapalı.",
        "all_files_access_on": "Tüm dosya erişimi açık.",
        "all_files_access_off": "Tüm dosya erişimi kapalı.",
        "play_store_open_failed": "Play Store açılamadı.",
        "settings_open_failed": "Ayarlar açılamadı.",
    },
    "en": {
        "app_ready": "Ready.",
        "settings": "Settings",
        "language": "Language",
        "select_language": "Select Language",
        "language_saved": "Language saved.",
        "language_updated": "Language updated.",
        "file_not_selected": "No file selected",
        "file_info_placeholder": "Selected document details will appear here.",
        "file_waiting": "Please select a document.",
        "file_selected_auto_scan": "Document selected • Scan starts automatically.",
        "select_file": "Select File",
        "test": "Test",
        "scan_completed": "Scan completed.",
        "update": "Update",
        "new_version_available": "A new version is available.",
        "open_list": "Open List",
        "session_restored": "Session restored.",
        "previous_session_restored": "Previous session restored.",
        "all_files_access_open": "All files access is enabled.",
        "all_files_access_closed": "All files access is disabled.",
        "all_files_access_on": "All files access is enabled.",
        "all_files_access_off": "All files access is disabled.",
        "play_store_open_failed": "Play Store could not be opened.",
        "settings_open_failed": "Settings could not be opened.",
    },
    "de": {
        "app_ready": "Bereit.",
        "settings": "Einstellungen",
        "language": "Sprache",
        "select_language": "Sprache auswählen",
        "language_saved": "Sprache gespeichert.",
        "language_updated": "Sprache aktualisiert.",
        "file_not_selected": "Keine Datei ausgewählt",
        "file_info_placeholder": (
            "Informationen zum ausgewählten Dokument werden hier angezeigt."
        ),
        "file_waiting": "Bitte wählen Sie ein Dokument aus.",
        "file_selected_auto_scan": "Dokument ausgewählt • Scan startet automatisch.",
        "select_file": "Datei auswählen",
        "test": "Test",
        "scan_completed": "Scan abgeschlossen.",
        "update": "Aktualisieren",
        "new_version_available": "Eine neue Version ist verfügbar.",
        "open_list": "Liste öffnen",
        "session_restored": "Sitzung wiederhergestellt.",
        "previous_session_restored": "Vorherige Sitzung wiederhergestellt.",
        "all_files_access_open": "Zugriff auf alle Dateien ist aktiviert.",
        "all_files_access_closed": "Zugriff auf alle Dateien ist deaktiviert.",
        "all_files_access_on": "Zugriff auf alle Dateien ist aktiviert.",
        "all_files_access_off": "Zugriff auf alle Dateien ist deaktiviert.",
        "play_store_open_failed": "Play Store konnte nicht geöffnet werden.",
        "settings_open_failed": "Einstellungen konnten nicht geöffnet werden.",
    },
}


# =========================================================
# INTERNAL HELPERS
# =========================================================
def _normalize_language_code(code: str | None) -> str:
    temiz = str(code or "").strip().lower()
    if not temiz:
        return DEFAULT_LANGUAGE

    temiz = temiz.replace("_", "-")

    if temiz in DIL_BILGILERI:
        return temiz

    if "-" in temiz:
        temel = temiz.split("-", 1)[0].strip()
        if temel in DIL_BILGILERI:
            return temel

    return DEFAULT_LANGUAGE


def _aktif_metin_sozlugu() -> dict[str, str]:
    kod = aktif_dil()
    data = METINLER.get(kod)
    return data if isinstance(data, dict) else {}


def _ingilizce_sozluk() -> dict[str, str]:
    data = METINLER.get("en")
    return data if isinstance(data, dict) else {}


def _turkce_sozluk() -> dict[str, str]:
    data = METINLER.get("tr")
    return data if isinstance(data, dict) else {}


# =========================================================
# PUBLIC API
# =========================================================
def aktif_dil() -> str:
    kod = str(get_language(default=DEFAULT_LANGUAGE) or DEFAULT_LANGUAGE).strip()
    return _normalize_language_code(kod)


def desteklenen_diller(
    sadece_aktifler: bool = False,
) -> dict[str, dict[str, object]]:
    desteklenen = set(supported_languages())
    sonuc: dict[str, dict[str, object]] = {}

    for kod in desteklenen:
        bilgi = DIL_BILGILERI.get(
            kod,
            {
                "ad": kod,
                "yerel_ad": kod,
                "aktif": False,
            },
        )

        try:
            if sadece_aktifler and not bool(bilgi.get("aktif", False)):
                continue
        except Exception:
            if sadece_aktifler:
                continue

        sonuc[kod] = dict(bilgi)

    return sonuc


def dil_var_mi(code: str) -> bool:
    kod = _normalize_language_code(code)
    return kod in desteklenen_diller(sadece_aktifler=False)


def dil_adi(code: str, default: str = "") -> str:
    kod = _normalize_language_code(code)
    try:
        bilgiler = desteklenen_diller(sadece_aktifler=False)
        return str(bilgiler[kod].get("yerel_ad") or default or kod)
    except Exception:
        return str(default or kod)


def metin(anahtar: str, default: str = "") -> str:
    key = str(anahtar or "").strip()
    if not key:
        return str(default or "")

    try:
        aktif_sozluk = _aktif_metin_sozlugu()
        if key in aktif_sozluk:
            return str(aktif_sozluk[key])

        en_sozluk = _ingilizce_sozluk()
        if key in en_sozluk:
            return str(en_sozluk[key])

        tr_sozluk = _turkce_sozluk()
        if key in tr_sozluk:
            return str(tr_sozluk[key])

        return str(default or key)
    except Exception:
        return str(default or key)