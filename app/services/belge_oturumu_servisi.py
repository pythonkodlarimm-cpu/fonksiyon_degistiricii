# -*- coding: utf-8 -*-
"""
DOSYA: app/services/belge_oturumu_servisi.py

ROL:
- Belge oturumunu başlatmak
- Çalışma kopyası bilgisini yönetmek
- Session kimliği ve görünen adını sağlamak
- Güncellenmiş içeriği kaydetmek
- Son yedek yolunu döndürmek

MİMARİ:
- Girdi: DocumentSelection veya DocumentSession
- İçe aktarma ve dışa yazma işlemlerini alt servislere delege eder
- Çalışma kopyası mantığını tek merkezden yönetir

API UYUMLULUK DEĞERLENDİRMESİ:
- Bu servis doğrudan Android API çağrısı yapmaz
- Android/URI/path farklarını alt servisler yönetir
- Bu nedenle yapısal olarak API 30+ ile uyumlu çalışmaya uygundur
- Bu düzenlenmiş sürüm API 34 hedeflenerek daha güvenli hale getirilmiştir

SURUM: 2
TARIH: 2026-03-17
IMZA: FY.
"""

from __future__ import annotations

from app.services.belge_disari_yazma_servisi import belgeyi_disari_yaz
from app.services.belge_ice_aktarma_servisi import belgeyi_ice_aktar
from app.services.dosya_servisi import exists
from app.ui.dosya_secici_paketi.models import DocumentSelection, DocumentSession


class BelgeOturumuServisiHatasi(ValueError):
    """Belge oturumu işlemleri sırasında oluşan kontrollü hata."""


def oturum_baslat(selection: DocumentSelection) -> DocumentSession:
    """
    Verilen belge seçimi için yeni bir oturum başlatır.

    İş akışı:
    1) seçim doğrulanır
    2) belge içe aktarılır
    3) çalışma kopyası oluştu mu kontrol edilir
    4) session döndürülür

    API 34 uyumluluk notu:
    - Android document URI veya filesystem farkı alt serviste çözülür.
    """
    if selection is None:
        raise BelgeOturumuServisiHatasi("Belge seçimi boş.")

    try:
        session = belgeyi_ice_aktar(selection)
    except Exception as exc:
        raise BelgeOturumuServisiHatasi(
            f"Oturum başlatılamadı: {exc}"
        ) from exc

    try:
        if session is None or not session.has_working_local_path():
            raise BelgeOturumuServisiHatasi("Çalışma kopyası oluşturulamadı.")
    except BelgeOturumuServisiHatasi:
        raise
    except Exception as exc:
        raise BelgeOturumuServisiHatasi(
            f"Çalışma kopyası doğrulanamadı: {exc}"
        ) from exc

    return session


def oturum_identifier(session: DocumentSession) -> str:
    """
    Session için öncelikli tanımlayıcıyı döndürür.

    Öncelik:
    1) preferred_source_identifier
    2) working_local_path

    API 34 uyumluluk notu:
    - Android URI tabanlı oturumlarda da güvenli tanımlayıcı üretir.
    """
    if session is None:
        return ""

    try:
        source_id = str(session.preferred_source_identifier() or "").strip()
        if source_id:
            return source_id
    except Exception:
        pass

    try:
        return str(getattr(session, "working_local_path", "") or "").strip()
    except Exception:
        return ""


def oturum_display_name(session: DocumentSession) -> str:
    """
    Session için görünen adı döndürür.

    API 34 uyumluluk notu:
    - URI veya path kaynağından türetilmiş adı güvenli şekilde taşır.
    """
    if session is None:
        return ""

    try:
        return str(session.preferred_display_name() or "").strip()
    except Exception:
        return ""


def calisma_dosyasi_yolu(session: DocumentSession) -> str:
    """
    Session içindeki çalışma kopyası yolunu döndürür.

    API 34 uyumluluk notu:
    - Çalışma kopyası uygulamanın yerel alanında tutulur.
    """
    if session is None:
        return ""

    try:
        return str(getattr(session, "working_local_path", "") or "").strip()
    except Exception:
        return ""


def calisma_kopyasi_var_mi(session: DocumentSession) -> bool:
    """
    Çalışma kopyası fiziksel olarak mevcut mu kontrol eder.

    API 34 uyumluluk notu:
    - Yerel çalışma kopyası dosya sistemi üzerinden doğrulanır.
    """
    yol = calisma_dosyasi_yolu(session)
    if not yol:
        return False

    try:
        return bool(exists(yol))
    except Exception:
        return False


def guncellenmis_icerigi_kaydet(session: DocumentSession, new_content: str) -> str:
    """
    Güncellenmiş belge içeriğini kaydeder ve yedek yolunu döndürür.

    İş akışı:
    1) session doğrulanır
    2) içerik doğrulanır
    3) dışa yazma servisi çağrılır
    4) oluşan yedek yolu döndürülür

    API 34 uyumluluk notu:
    - Android URI kaynağı varsa alt servis SAF/URI akışını kullanır.
    """
    if session is None:
        raise BelgeOturumuServisiHatasi("Session boş.")

    icerik = str(new_content or "")
    if not icerik.strip():
        raise BelgeOturumuServisiHatasi("Yeni içerik boş olamaz.")

    try:
        return str(belgeyi_disari_yaz(session, icerik) or "").strip()
    except Exception as exc:
        raise BelgeOturumuServisiHatasi(
            f"Kaydetme başarısız: {exc}"
        ) from exc


def son_yedek_yolu(session: DocumentSession) -> str:
    """
    Session içindeki son yedek yolunu döndürür.

    API 34 uyumluluk notu:
    - Yedek yolu uygulamanın kontrol ettiği çalışma alanına aittir.
    """
    if session is None:
        return ""

    try:
        return str(getattr(session, "last_backup_path", "") or "").strip()
    except Exception:
        return ""