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

# ✅ Play Store + AdMob + Network
android.permissions = INTERNET,ACCESS_NETWORK_STATE,com.google.android.gms.permission.AD_ID,READ_EXTERNAL_STORAGE,(name=android.permission.WRITE_EXTERNAL_STORAGE;maxSdkVersion=28)

# ✅ Android hedefleri (Play Store 2026 uyumlu)
android.api = 35
android.minapi = 23

# ✅ SDK yolları
android.sdk_path = /usr/local/lib/android/sdk
android.ndk_path = /usr/local/lib/android/sdk/ndk/28.2.13676358
android.ant_path = /usr/share/ant

# ✅ AndroidX zorunlu
android.enable_androidx = True

# ✅ Google Play güvenlik uyumları
android.allow_backup = False
android.accept_sdk_license = True

# ✅ Build çıktısı android.yml kontrol edecek
android.release_artifact = apk

# ✅ AdMob
android.gradle_dependencies = com.google.android.gms:play-services-ads:22.6.0
android.meta_data = com.google.android.gms.ads.APPLICATION_ID=ca-app-pub-5522917995813710~6900495663

# ✅ Custom manifest
android.add_src = .android

# ✅ ARM destekleri (Play Store zorunlu)
android.archs = arm64-v8a, armeabi-v7a

# ✅ Log
log_level = 2

[buildozer]
log_level = 2
warn_on_root = 1
