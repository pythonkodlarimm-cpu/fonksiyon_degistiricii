[app]

title = Fonksiyon Degistirici
package.name = fonksiyon_degistirici
package.domain = org.fy

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt,ttf,xml
source.exclude_exts = pyc,pyo,log,md
source.exclude_dirs = .git,.github,__pycache__,bin,.buildozer,venv,.venv,tests
source.exclude_patterns = *.bak,*.tmp,*.swp,.DS_Store

version = 0.1.1
android.numeric_version = 1

requirements = python3,kivy,pygments,pyjnius

orientation = portrait
fullscreen = 0

icon.filename = app/assets/icons/app_icon.png
presplash.filename = app/assets/icons/presplash.png

# Play Console + AdMob
android.permissions = INTERNET,ACCESS_NETWORK_STATE,com.google.android.gms.permission.AD_ID

# Play 2026 hedefleri
android.api = 35
android.minapi = 23

# SDK / NDK
android.sdk_path = /usr/local/lib/android/sdk
android.ndk_path = /usr/local/lib/android/sdk/ndk/25.2.9519653
android.ant_path = /usr/share/ant

# AndroidX
android.enable_androidx = True

# Güvenlik / yedek
android.allow_backup = False
android.accept_sdk_license = True

# Play için ana çıktı
android.release_artifact = aab

# AdMob
android.gradle_dependencies = com.google.android.gms:play-services-ads:22.6.0
android.meta_data = com.google.android.gms.ads.APPLICATION_ID=ca-app-pub-5522917995813710~6900495663

# Özel manifest
android.add_src = .android

# Desteklenen mimariler
android.archs = arm64-v8a, armeabi-v7a

log_level = 2

[buildozer]
log_level = 2
warn_on_root = 1
