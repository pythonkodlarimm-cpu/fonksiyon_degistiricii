[app]

title = Fonksiyon Degistirici
package.name = fonksiyon_degistirici
package.domain = org.fy

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt,ttf
source.exclude_exts = pyc,pyo,log,md
source.exclude_dirs = .git,.github,__pycache__,bin,.buildozer,venv,.venv,tests
source.exclude_patterns = *.bak,*.tmp,*.swp,.DS_Store

version = 0.1.0

requirements = python3,kivy,pygments

orientation = portrait
fullscreen = 0

icon.filename = app/assets/icons/app_icon.png
presplash.filename = app/assets/icons/presplash.png

android.permissions = READ_EXTERNAL_STORAGE,(name=android.permission.WRITE_EXTERNAL_STORAGE;maxSdkVersion=28)

android.api = 31
android.minapi = 21

android.accept_sdk_license = True
android.enable_androidx = True
android.allow_backup = True

log_level = 2

[buildozer]
log_level = 2
warn_on_root = 1
