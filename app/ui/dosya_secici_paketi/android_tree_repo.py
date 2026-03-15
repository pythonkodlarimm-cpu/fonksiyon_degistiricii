# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dosya_secici_paketi/android_tree_repo.py

ROL:
- Android Storage Access Framework tree erişim katmanı
- Tree URI üzerinden klasör ve dosyaları listeler
- Seçilen dosyayı uygulama cache alanına kopyalar

NOT:
- Path yerine DocumentFile tabanlı erişim kullanır
- Seçilen klasörün kalıcı okuma izni alınır
- Seçilen dosya geçici dosyaya kopyalanarak mevcut tarama akışına uyarlanır
- Debug log güçlendirilmiştir

SURUM: 2
TARIH: 2026-03-15
IMZA: FY.
"""

from __future__ import annotations

from pathlib import Path


class AndroidTreeRepo:
    def __init__(self, owner):
        self.owner = owner

    # ---------------------------------------------------------
    # debug
    # ---------------------------------------------------------
    def _debug(self, message: str) -> None:
        try:
            self.owner._debug(f"[TREE_REPO] {message}")
        except Exception:
            try:
                print("[ANDROID_TREE_REPO]", str(message))
            except Exception:
                pass

    # ---------------------------------------------------------
    # android sınıfları
    # ---------------------------------------------------------
    def _classes(self):
        from jnius import autoclass, cast  # type: ignore

        Intent = autoclass("android.content.Intent")
        Uri = autoclass("android.net.Uri")
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        DocumentFile = autoclass("androidx.documentfile.provider.DocumentFile")

        current_activity = cast("android.app.Activity", PythonActivity.mActivity)
        resolver = current_activity.getContentResolver()

        return {
            "Intent": Intent,
            "Uri": Uri,
            "PythonActivity": PythonActivity,
            "DocumentFile": DocumentFile,
            "activity": current_activity,
            "resolver": resolver,
        }

    # ---------------------------------------------------------
    # yardımcılar
    # ---------------------------------------------------------
    def _safe_name(self, doc) -> str:
        try:
            return str(doc.getName() or "").strip()
        except Exception:
            return ""

    def _safe_uri_str(self, doc) -> str:
        try:
            return str(doc.getUri() or "")
        except Exception:
            return ""

    def _safe_exists(self, doc) -> bool:
        try:
            return bool(doc is not None and doc.exists())
        except Exception:
            return False

    def _safe_is_dir(self, doc) -> bool:
        try:
            return bool(doc is not None and doc.isDirectory())
        except Exception:
            return False

    def _safe_is_file(self, doc) -> bool:
        try:
            return bool(doc is not None and doc.isFile())
        except Exception:
            return False

    # ---------------------------------------------------------
    # tree
    # ---------------------------------------------------------
    def take_persistable_permission(self, intent, tree_uri) -> None:
        if intent is None or tree_uri is None:
            self._debug("Persistable izin için intent veya tree_uri boş")
            return

        ctx = self._classes()
        Intent = ctx["Intent"]
        resolver = ctx["resolver"]

        try:
            flags = intent.getFlags()
            take_flags = (
                flags
                & (
                    Intent.FLAG_GRANT_READ_URI_PERMISSION
                    | Intent.FLAG_GRANT_WRITE_URI_PERMISSION
                )
            )
            resolver.takePersistableUriPermission(tree_uri, take_flags)
            self._debug("Persistable tree izni alındı")
        except Exception as exc:
            self._debug(f"Persistable tree izni alınamadı: {exc}")

    def get_root_doc(self, tree_uri):
        ctx = self._classes()
        DocumentFile = ctx["DocumentFile"]
        activity = ctx["activity"]

        try:
            root_doc = DocumentFile.fromTreeUri(activity, tree_uri)
            self._debug(
                "fromTreeUri sonucu | "
                f"name={self._safe_name(root_doc)} "
                f"uri={self._safe_uri_str(root_doc)} "
                f"exists={self._safe_exists(root_doc)} "
                f"is_dir={self._safe_is_dir(root_doc)}"
            )
            return root_doc
        except Exception as exc:
            self._debug(f"fromTreeUri hatası: {exc}")
            return None

    def list_children(self, directory_doc):
        """
        directory_doc içindeki öğeleri listeler.
        Dönen listede:
        - klasörler önce
        - .py dosyaları sonra
        - diğer dosyalar en sonda gelir
        """
        sonuc = []

        if directory_doc is None:
            self._debug("list_children: directory_doc None")
            return sonuc

        self._debug(
            "list_children başladı | "
            f"name={self._safe_name(directory_doc)} "
            f"uri={self._safe_uri_str(directory_doc)} "
            f"exists={self._safe_exists(directory_doc)} "
            f"is_dir={self._safe_is_dir(directory_doc)}"
        )

        if not self._safe_exists(directory_doc):
            self._debug("list_children: directory_doc exists=False")
            return sonuc

        if not self._safe_is_dir(directory_doc):
            self._debug("list_children: directory_doc klasör değil")
            return sonuc

        try:
            children = directory_doc.listFiles()
        except Exception as exc:
            self._debug(f"listFiles hatası: {exc}")
            return sonuc

        try:
            toplam = len(children)
        except Exception:
            toplam = -1

        self._debug(f"listFiles döndü | adet={toplam}")

        klasorler = []
        py_dosyalar = []
        diger_dosyalar = []

        for idx, child in enumerate(children):
            try:
                name = self._safe_name(child)
                uri_str = self._safe_uri_str(child)
                is_dir = self._safe_is_dir(child)
                is_file = self._safe_is_file(child)
                exists = self._safe_exists(child)

                self._debug(
                    f"child[{idx}] | "
                    f"name={name} "
                    f"exists={exists} "
                    f"is_dir={is_dir} "
                    f"is_file={is_file} "
                    f"uri={uri_str}"
                )

                item = {
                    "name": name,
                    "uri": uri_str,
                    "doc": child,
                    "is_dir": is_dir,
                    "is_file": is_file,
                }

                if is_dir:
                    klasorler.append(item)
                elif is_file and name.lower().endswith(".py"):
                    py_dosyalar.append(item)
                elif is_file:
                    diger_dosyalar.append(item)
            except Exception as exc:
                self._debug(f"Öğe okunamadı: {exc}")

        klasorler.sort(key=lambda x: x["name"].lower())
        py_dosyalar.sort(key=lambda x: x["name"].lower())
        diger_dosyalar.sort(key=lambda x: x["name"].lower())

        sonuc.extend(klasorler)
        sonuc.extend(py_dosyalar)
        sonuc.extend(diger_dosyalar)

        self._debug(
            "list_children bitti | "
            f"klasor={len(klasorler)} "
            f"py={len(py_dosyalar)} "
            f"diger={len(diger_dosyalar)}"
        )

        return sonuc

    # ---------------------------------------------------------
    # cache
    # ---------------------------------------------------------
    def get_cache_root(self) -> Path:
        try:
            ctx = self._classes()
            activity = ctx["activity"]
            cache_dir = activity.getCacheDir()
            cache_path = str(cache_dir.getAbsolutePath())
            root = Path(cache_path) / "fonksiyon_degistirici_tree"
            root.mkdir(parents=True, exist_ok=True)
            self._debug(f"Tree cache root: {root}")
            return root
        except Exception as exc:
            self._debug(f"Tree cache fallback: {exc}")
            fallback = Path.cwd() / "fonksiyon_degistirici_tree"
            fallback.mkdir(parents=True, exist_ok=True)
            return fallback

    def materialize_file(self, file_doc, previous_temp_file: str = "") -> str:
        """
        DocumentFile dosyasını uygulama cache alanına kopyalar ve path döner.
        """
        if file_doc is None:
            self._debug("materialize_file: file_doc None")
            return ""

        input_stream = None

        try:
            ctx = self._classes()
            resolver = ctx["resolver"]

            name = self._safe_name(file_doc) or "secilen_dosya.py"
            uri = file_doc.getUri()

            self._debug(
                "materialize başladı | "
                f"name={name} "
                f"exists={self._safe_exists(file_doc)} "
                f"is_file={self._safe_is_file(file_doc)} "
                f"uri={self._safe_uri_str(file_doc)}"
            )

            input_stream = resolver.openInputStream(uri)

            if input_stream is None:
                self._debug("openInputStream None döndü")
                return ""

            cache_root = self.get_cache_root()
            target_path = cache_root / name

            if previous_temp_file:
                try:
                    eski = Path(previous_temp_file)
                    if eski.exists() and eski.is_file():
                        eski.unlink()
                        self._debug(f"Eski temp silindi: {eski}")
                except Exception as exc:
                    self._debug(f"Eski temp silinemedi: {exc}")

            toplam_yazilan = 0

            with open(target_path, "wb") as out_file:
                while True:
                    byte_val = input_stream.read()
                    if byte_val == -1:
                        break
                    out_file.write(bytes([byte_val]))
                    toplam_yazilan += 1

            self._debug(f"Yazılan byte: {toplam_yazilan}")

            if toplam_yazilan <= 0:
                try:
                    if target_path.exists():
                        target_path.unlink()
                except Exception:
                    pass
                self._debug("0 byte yazıldı, temp silindi")
                return ""

            try:
                exists_after = target_path.exists()
                is_file_after = target_path.is_file()
                size_after = target_path.stat().st_size if exists_after else -1
            except Exception:
                exists_after = False
                is_file_after = False
                size_after = -1

            self._debug(
                "materialize tamam | "
                f"path={target_path} "
                f"exists={exists_after} "
                f"is_file={is_file_after} "
                f"size={size_after}"
            )

            return str(target_path)

        except Exception as exc:
            self._debug(f"Dosya cache'e kopyalanamadı: {exc}")
            return ""
        finally:
            try:
                if input_stream is not None:
                    input_stream.close()
            except Exception:
                pass