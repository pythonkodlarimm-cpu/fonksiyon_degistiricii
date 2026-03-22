# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/yedek/dosya_yolu_acici.py

ROL:
- Verilen dosya veya klasör yolunu Android dosya yöneticisinde açmak
- Yedek indirme sonrası kullanıcıya hızlı erişim sağlamak

MİMARİ:
- Android bağımlılığı izole edilmiştir
- Platform kontrolü içerir
- Hata durumunda False döner (UI kırılmaz)

API UYUMLULUK:
- Sadece Android'de aktif çalışır
- Android API 35 ile uyumludur
- Android 7+ için FileProvider kullanır
- Gerekirse eski fallback yaklaşımı uygular

NOT:
- AndroidManifest içinde FileProvider tanımı olmalıdır
- .android/res/xml/file_paths.xml dosyası eklenmelidir

SURUM: 3
TARIH: 2026-03-22
IMZA: FY.
"""

from __future__ import annotations

from pathlib import Path

from kivy.utils import platform


def open_path_in_file_manager(path_value: str | Path, debug=None) -> bool:
    """
    Verilen path'i Android dosya yöneticisinde açar.

    Parametre:
    - path_value: dosya veya klasör yolu
    - debug: opsiyonel debug callback

    Dönüş:
    - True → başarı
    - False → başarısız
    """

    if platform != "android":
        return False

    try:
        from jnius import autoclass
        from android import mActivity

        path_obj = Path(str(path_value or "").strip())

        if not path_obj.exists():
            if callable(debug):
                debug(f"Path bulunamadı: {path_obj}")
            return False

        hedef = path_obj.parent if path_obj.is_file() else path_obj

        File = autoclass("java.io.File")
        Intent = autoclass("android.content.Intent")
        Uri = autoclass("android.net.Uri")
        Build = autoclass("android.os.Build")
        FileProvider = autoclass("androidx.core.content.FileProvider")

        java_file = File(str(hedef))
        intent = Intent(Intent.ACTION_VIEW)
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)

        uri = None

        # Android 7+ için güvenli yol
        if Build.VERSION.SDK_INT >= 24:
            try:
                context = mActivity.getApplicationContext()
                package_name = context.getPackageName()

                uri = FileProvider.getUriForFile(
                    context,
                    f"{package_name}.fileprovider",
                    java_file,
                )

                intent.setDataAndType(uri, "*/*")

            except Exception as exc:
                if callable(debug):
                    debug(f"FileProvider ile açma başarısız, fallback deneniyor: {exc}")

        # Fallback
        if uri is None:
            uri = Uri.fromFile(java_file)
            intent.setDataAndType(uri, "*/*")

        chooser = Intent.createChooser(intent, "Konumu Aç")
        chooser.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)

        mActivity.startActivity(chooser)
        return True

    except Exception as exc:
        if callable(debug):
            debug(f"Dosya yöneticisi açma hatası: {exc}")
        return False