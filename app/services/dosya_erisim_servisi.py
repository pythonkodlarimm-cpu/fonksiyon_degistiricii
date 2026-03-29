# -*- coding: utf-8 -*-
"""
DOSYA: app/services/dosya_erisim_servisi.py

ROL:
- Normal dosya yolu ve Android document URI erişimini tek API altında birleştirir
- Metin okuma / yazma işlemlerini kaynak tipine göre doğru katmana yönlendirir
- UI ve üst servis katmanlarının path / content:// ayrımını bilmesini engeller
- Android SAF akışına geçişi kolaylaştırır

MİMARİ:
- Thin orchestration service
- Path ve Android URI erişimini tek noktada toplar
- Deterministik davranır
- Lazy resolve kullanır
- Type güvenliği yüksektir
- Geriye uyumluluk katmanı içermez

DESTEK:
- Normal path: /storage/emulated/0/... veya göreli/absolute dosya yolu
- Android URI: content://...
- Text read/write
- Display name çözümü
- MIME type çözümü
- Persistable URI permission alma
- App files/cache dizini çözümü

API UYUMLULUK:
- Platform bağımsız
- Android API 35 uyumlu
- Pydroid3 / masaüstü / test ortamı uyumlu
- Android tarafında SAF/URI erişimiyle uyumludur

SURUM: 2
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from pathlib import Path

from kivy.utils import platform


class DosyaErisimServisiHatasi(ValueError):
    """
    Dosya erişim katmanında oluşan kontrollü hata.
    """


class DosyaErisimServisi:
    """
    Path ve Android URI erişimini birleştiren servis katmanı.
    """

    __slots__ = (
        "_uri_modul",
    )

    def __init__(self) -> None:
        self._uri_modul = None

    # =========================================================
    # INTERNAL
    # =========================================================
    def _uri(self):
        """
        Android URI servis modülünü lazy load eder.
        """
        modul = self._uri_modul
        if modul is None:
            from app.services.android import uri_servisi

            modul = uri_servisi
            self._uri_modul = modul
        return modul

    def _normalize_value(self, value: str | Path) -> str:
        raw = str(value or "").strip()
        if not raw:
            raise DosyaErisimServisiHatasi("Kaynak boş olamaz.")
        return raw

    def _is_android_uri(self, value: str | Path) -> bool:
        raw = self._normalize_value(value)

        if not raw.startswith("content://"):
            return False

        # Test/mocked kullanım desteği:
        # Eğer uri modülü dışarıdan enjekte edilmişse platform kontrolüne takılmadan
        # doğrudan o modül üzerinden karar ver.
        if self._uri_modul is not None:
            try:
                return bool(self._uri().is_android_document_uri(raw))
            except Exception:
                return False

        # Gerçek çözümleme yalnızca Android üzerinde yapılır.
        if platform != "android":
            return False

        try:
            return bool(self._uri().is_android_document_uri(raw))
        except Exception:
            return False

    def _path_obj(self, value: str | Path) -> Path:
        raw = self._normalize_value(value)
        return Path(raw)

    def _ensure_file_path_exists(self, path_obj: Path) -> None:
        if not path_obj.exists():
            raise DosyaErisimServisiHatasi(f"Dosya bulunamadı: {path_obj}")

        if not path_obj.is_file():
            raise DosyaErisimServisiHatasi(f"Geçerli bir dosya değil: {path_obj}")

    # =========================================================
    # TYPE / INFO
    # =========================================================
    def android_uri_mi(self, value: str | Path) -> bool:
        """
        Verilen kaynağın Android document URI olup olmadığını döndürür.
        """
        return self._is_android_uri(value)

    def kaynak_tipi(self, value: str | Path) -> str:
        """
        Kaynak tipini döndürür.

        Returns:
            "android_uri" | "path"
        """
        return "android_uri" if self._is_android_uri(value) else "path"

    def gorunen_ad(self, value: str | Path) -> str:
        """
        Kaynağın kullanıcıya gösterilecek adını döndürür.
        """
        raw = self._normalize_value(value)

        if self._is_android_uri(raw):
            try:
                return str(self._uri().get_display_name(raw) or "").strip() or raw
            except Exception as exc:
                raise DosyaErisimServisiHatasi(
                    "Android URI görünen adı alınamadı."
                ) from exc

        return self._path_obj(raw).name

    def mime_type(self, value: str | Path) -> str:
        """
        Kaynağın mime type bilgisini döndürür.
        Path kaynaklarında suffix bazlı tahmin yapmaz; boş string döner.
        """
        raw = self._normalize_value(value)

        if self._is_android_uri(raw):
            try:
                return str(self._uri().get_mime_type(raw) or "").strip()
            except Exception as exc:
                raise DosyaErisimServisiHatasi(
                    "Android URI mime type alınamadı."
                ) from exc

        return ""

    # =========================================================
    # PERMISSION
    # =========================================================
    def kalici_izin_al(self, intent, uri: str | Path) -> None:
        """
        Android document URI için persistable permission almaya çalışır.
        """
        raw = self._normalize_value(uri)

        if not self._is_android_uri(raw):
            raise DosyaErisimServisiHatasi(
                "Kalıcı izin yalnızca Android document URI için alınabilir."
            )

        try:
            self._uri().take_persistable_permission(intent, raw)
        except Exception as exc:
            raise DosyaErisimServisiHatasi(
                "Kalıcı URI izni alınamadı."
            ) from exc

    # =========================================================
    # READ
    # =========================================================
    def metin_oku(
        self,
        kaynak: str | Path,
        *,
        encoding: str = "utf-8",
    ) -> str:
        """
        Verilen kaynaktan metin okur.
        """
        raw = self._normalize_value(kaynak)

        if self._is_android_uri(raw):
            try:
                return str(self._uri().read_text(raw, encoding=encoding))
            except Exception as exc:
                raise DosyaErisimServisiHatasi(
                    "Android URI metin okuma hatası."
                ) from exc

        path_obj = self._path_obj(raw)
        self._ensure_file_path_exists(path_obj)

        try:
            return path_obj.read_text(encoding=encoding)
        except UnicodeDecodeError as exc:
            raise DosyaErisimServisiHatasi(
                f"Dosya '{encoding}' ile okunamadı: {path_obj}"
            ) from exc
        except OSError as exc:
            raise DosyaErisimServisiHatasi(
                f"Dosya okunamadı: {path_obj}"
            ) from exc

    # =========================================================
    # WRITE
    # =========================================================
    def metin_yaz(
        self,
        kaynak: str | Path,
        icerik: str,
        *,
        encoding: str = "utf-8",
    ) -> None:
        """
        Verilen kaynağa metin yazar.
        """
        raw = self._normalize_value(kaynak)
        text = str(icerik or "")

        if self._is_android_uri(raw):
            try:
                self._uri().write_text(raw, text, encoding=encoding)
                return
            except Exception as exc:
                raise DosyaErisimServisiHatasi(
                    "Android URI metin yazma hatası."
                ) from exc

        path_obj = self._path_obj(raw)

        try:
            parent = path_obj.parent
            if parent and not parent.exists():
                parent.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            raise DosyaErisimServisiHatasi(
                f"Hedef klasör hazırlanamadı: {path_obj}"
            ) from exc

        try:
            path_obj.write_text(text, encoding=encoding)
        except OSError as exc:
            raise DosyaErisimServisiHatasi(
                f"Dosyaya yazılamadı: {path_obj}"
            ) from exc

    # =========================================================
    # APP DIRS
    # =========================================================
    def app_cache_dizini(self) -> Path:
        """
        Uygulama cache dizinini döndürür.
        Android'de URI servisi üzerinden, diğer ortamlarda yerel fallback ile çalışır.
        """
        if platform == "android" or self._uri_modul is not None:
            try:
                return self._uri().get_app_cache_dir()
            except Exception as exc:
                raise DosyaErisimServisiHatasi(
                    "Android app cache dizini alınamadı."
                ) from exc

        fallback = Path(".cache").resolve()
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback

    def app_files_dizini(self) -> Path:
        """
        Uygulama files dizinini döndürür.
        Android'de URI servisi üzerinden, diğer ortamlarda yerel fallback ile çalışır.
        """
        if platform == "android" or self._uri_modul is not None:
            try:
                return self._uri().get_app_files_dir()
            except Exception as exc:
                raise DosyaErisimServisiHatasi(
                    "Android app files dizini alınamadı."
                ) from exc

        fallback = Path(".files").resolve()
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback