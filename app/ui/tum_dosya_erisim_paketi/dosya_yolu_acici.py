# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from kivy.utils import platform


def open_path_in_file_manager(path_value: str | Path) -> bool:
    if platform != "android":
        return False

    try:
        from jnius import autoclass
        from android import mActivity

        path_obj = Path(str(path_value or "").strip())
        if not path_obj.exists():
            return False

        File = autoclass("java.io.File")
        Intent = autoclass("android.content.Intent")
        Uri = autoclass("android.net.Uri")

        intent = Intent(Intent.ACTION_VIEW)
        java_file = File(str(path_obj.parent if path_obj.is_file() else path_obj))
        uri = Uri.fromFile(java_file)

        intent.setDataAndType(uri, "*/*")
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)

        mActivity.startActivity(intent)
        return True
    except Exception:
        return False