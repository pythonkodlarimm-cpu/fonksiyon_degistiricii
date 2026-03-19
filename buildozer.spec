[app]

title = Fonksiyon Degistirici
package.name = fonksiyon_degistirici
package.domain = org.fy

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt,ttf
source.exclude_exts = pyc,pyo,log,md
source.exclude_dirs = .git,.github,__pycache__,bin,.buildozer,venv,.venv,tests
source.exclude_patterns = *.bak,*.tmp,*.swp,.DS_Store

version = 0.1.1

requirements = python3,kivy,pygments,pyjnius

orientation = all
fullscreen = 0

icon.filename = app/assets/icons/app_icon.png
presplash.filename = app/assets/icons/presplash.png

android.permissions = READ_EXTERNAL_STORAGE,(name=android.permission.WRITE_EXTERNAL_STORAGE;maxSdkVersion=28),INTERNET,ACCESS_NETWORK_STATE,com.google.android.gms.permission.AD_ID

android.api = 35
android.minapi = 23

android.sdk_path = /usr/local/lib/android/sdk
android.ant_path = /usr/share/ant

android.accept_sdk_license = True
android.enable_androidx = True
android.allow_backup = True
android.release_artifact = apk

android.gradle_dependencies = com.google.android.gms:play-services-ads:22.6.0,androidx.fragment:fragment:1.8.9
android.meta_data = com.google.android.gms.ads.APPLICATION_ID=ca-app-pub-5522917995813710~6900495663

log_level = 2

[buildozer]
log_level = 2
warn_on_root = 1
