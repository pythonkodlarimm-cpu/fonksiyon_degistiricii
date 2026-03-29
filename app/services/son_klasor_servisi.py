# -*- coding: utf-8 -*-
"""
DOSYA: app/services/son_klasor_servisi.py

ROL:
- Kullanıcının en son kaldığı klasör / başlangıç kaynağını saklar
- Android SAF URI veya normal dosya yolu için tek bir kalıcı kayıt noktası sağlar
- Bir sonraki picker açılışında başlangıç konumunu döndürür

MİMARİ:
- File-based storage (JSON)
- Atomic write
- Lazy dependency resolve
- Android URI ve normal path ayrımını servis içinde çözer
- Deterministik davranır
- Type güvenliği yüksektir
- Geriye uyumluluk katmanı içermez

NOT:
- Android'de content:// URI seçildiyse bu değer saklanır
- Normal path seçildiyse parent klasör saklanır
- UI katmanı sadece bu servisten başlangıç kaynağını ister
- URI değerleri Path(...) içine zorlanmaz

API UYUMLULUK:
- Platform bağımsız
- Android API 35 uyumlu
- Pydroid3 / masaüstü / test ortamı uyumlu

SURUM: 2
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from kivy.utils import platform


class SonKlasorServisiHatasi(ValueError):
    """
    Son klasör servisi işlemlerinde oluşan kontrollü hata.
    """


class SonKlasorServisi:
    """
    Son seçilen klasör / picker başlangıç kaynağı servis katmanı.
    """

    __slots__ = (
        "_android",
    )

    def __init__(self) -> None:
        self._android = None

    # =========================================================
    # INTERNAL
    # =========================================================
    def _android_yoneticisi(self):
        obj = self._android
        if obj is None:
            from app.services.android import AndroidYoneticisi

            obj = AndroidYoneticisi()
            self._android = obj
        return obj

    def _normalize_value(self, value: str | Path) -> str:
        raw = str(value or "").strip()
        if not raw:
            raise SonKlasorServisiHatasi("Kaynak boş olamaz.")
        return raw

    def _is_android_uri(self, value: str | Path) -> bool:
        raw = self._normalize_value(value)

        if not raw.startswith("content://"):
            return False

        # Test / mock desteği:
        # Android yöneticisi enjekte edilmişse platform gate'e takılmadan kullan.
        if self._android is not None:
            try:
                return bool(self._android_yoneticisi().is_android_document_uri(raw))
            except Exception:
                return False

        # Gerçek cihaz akışı
        if platform != "android":
            return False

        try:
            return bool(self._android_yoneticisi().is_android_document_uri(raw))
        except Exception:
            return False

    def _ayar_dizini(self) -> Path:
        if platform == "android":
            try:
                root = self._android_yoneticisi().get_app_files_dir() / "settings"
                root.mkdir(parents=True, exist_ok=True)
                return root
            except Exception as exc:
                raise SonKlasorServisiHatasi(
                    "Android app files/settings dizini hazırlanamadı."
                ) from exc

        root = Path(".settings").resolve()
        root.mkdir(parents=True, exist_ok=True)
        return root

    def _ayar_dosyasi(self) -> Path:
        return self._ayar_dizini() / "son_klasor.json"

    def _atomic_write_json(self, path_obj: Path, payload: dict) -> None:
        tmp = path_obj.with_suffix(path_obj.suffix + ".tmp")

        try:
            tmp.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            os.replace(str(tmp), str(path_obj))
        except Exception as exc:
            try:
                if tmp.exists():
                    tmp.unlink()
            except Exception:
                pass

            raise SonKlasorServisiHatasi(
                f"Ayar dosyası yazılamadı: {path_obj}"
            ) from exc

    def _read_payload(self) -> dict:
        path_obj = self._ayar_dosyasi()

        if not path_obj.exists():
            return {}

        try:
            data = json.loads(path_obj.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _normalize_picker_start_value(
        self,
        kaynak: str | Path,
        *,
        picker_baslangic_kaynagi: str | Path | None = None,
    ) -> str:
        """
        Saklanacak picker başlangıç kaynağını üretir.

        Öncelik:
        1) picker_baslangic_kaynagi verildiyse onu kullan
        2) Android URI ise doğrudan URI'yi sakla
        3) Normal path ise parent klasörü sakla
        """
        if picker_baslangic_kaynagi is not None:
            raw_picker = self._normalize_value(picker_baslangic_kaynagi)
            if self._is_android_uri(raw_picker):
                return raw_picker
            path_obj = Path(raw_picker)
            return str(path_obj.parent if path_obj.suffix else path_obj)

        raw = self._normalize_value(kaynak)

        if self._is_android_uri(raw):
            return raw

        path_obj = Path(raw)
        return str(path_obj.parent if path_obj.suffix else path_obj)

    # =========================================================
    # PUBLIC API
    # =========================================================
    def son_klasor_kaydet(
        self,
        kaynak: str | Path,
        *,
        picker_baslangic_kaynagi: str | Path | None = None,
    ) -> str:
        """
        Son seçilen klasör / başlangıç kaynağını kaydeder.

        Returns:
            Kaydedilen normalized başlangıç kaynağı
        """
        stored_value = self._normalize_picker_start_value(
            kaynak,
            picker_baslangic_kaynagi=picker_baslangic_kaynagi,
        )

        payload = {
            "value": stored_value,
            "kind": "android_uri" if self._is_android_uri(stored_value) else "path",
        }

        self._atomic_write_json(self._ayar_dosyasi(), payload)
        return stored_value

    def son_klasor_getir(self) -> str:
        """
        Kayıtlı başlangıç kaynağını döndürür.
        """
        payload = self._read_payload()
        value = payload.get("value")

        if not isinstance(value, str) or not value.strip():
            raise SonKlasorServisiHatasi("Kayıtlı son klasör bulunamadı.")

        return value.strip()

    def son_klasor_var_mi(self) -> bool:
        """
        Kayıtlı başlangıç kaynağı var mı?
        """
        payload = self._read_payload()
        value = payload.get("value")
        return isinstance(value, str) and bool(value.strip())

    def son_klasor_temizle(self) -> bool:
        """
        Kayıtlı başlangıç kaynağını siler.
        """
        path_obj = self._ayar_dosyasi()

        if not path_obj.exists():
            return False

        try:
            path_obj.unlink()
            return True
        except Exception as exc:
            raise SonKlasorServisiHatasi(
                "Son klasör kaydı silinemedi."
            ) from exc

    def picker_baslangic_kaynagi(self) -> str | None:
        """
        Picker açılışında kullanılacak başlangıç kaynağını döndürür.
        Kayıt yoksa None döner.
        """
        if not self.son_klasor_var_mi():
            return None

        try:
            return self.son_klasor_getir()
        except Exception:
            return None

    def android_picker_baslangic_uri(self) -> str | None:
        """
        Android SAF picker için kullanılabilecek başlangıç URI'sini döndürür.
        Kayıt path ise None döner.
        """
        value = self.picker_baslangic_kaynagi()
        if not value:
            return None

        if self._is_android_uri(value):
            return value

        return None