[app]

# ---------------------------------------------------------
# UYGULAMA TEMEL BILGILERI
# ---------------------------------------------------------
title = Fonksiyon Degistirici
package.name = fonksiyon_degistirici
package.domain = org.fy

# ---------------------------------------------------------
# KAYNAK DOSYALARI
# ---------------------------------------------------------
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt,ttf,xml
source.exclude_exts = pyc,pyo,log,md
source.exclude_dirs = .git,.github,__pycache__,bin,.buildozer,venv,.venv,tests
source.exclude_patterns = *.bak,*.tmp,*.swp,.DS_Store

# ---------------------------------------------------------
# SURUM
# ---------------------------------------------------------
version = 0.1.2
android.numeric_version = 2

# ---------------------------------------------------------
# GEREKSINIMLER
# ---------------------------------------------------------
requirements = python3,kivy,pygments,pyjnius

# ---------------------------------------------------------
# EKRAN / ORYANTASYON
# ---------------------------------------------------------
orientation = portrait
fullscreen = 0

# ---------------------------------------------------------
# IKON / ACILIS
# ---------------------------------------------------------
icon.filename = app/assets/icons/app_icon.png
presplash.filename = app/assets/icons/presplash.png

# ---------------------------------------------------------
# ANDROID IZINLERI
# ---------------------------------------------------------
android.permissions = INTERNET,ACCESS_NETWORK_STATE,com.google.android.gms.permission.AD_ID

# ---------------------------------------------------------
# ANDROID API AYARLARI
# ---------------------------------------------------------
android.api = 35
android.minapi = 23

# ---------------------------------------------------------
# SDK / NDK YOLLARI
# ---------------------------------------------------------
android.sdk_path = /usr/local/lib/android/sdk
android.ndk_path = /usr/local/lib/android/sdk/ndk/25.2.9519653
android.ant_path = /usr/share/ant

# ---------------------------------------------------------
# ANDROIDX
# ---------------------------------------------------------
android.enable_androidx = True

# ---------------------------------------------------------
# YEDEK / LISANS
# ---------------------------------------------------------
android.allow_backup = False
android.accept_sdk_license = True

# ---------------------------------------------------------
# CIKTI TURU
# ---------------------------------------------------------
android.release_artifact = aab

# ---------------------------------------------------------
# ADMOB / GOOGLE ADS
# ---------------------------------------------------------
android.gradle_dependencies = com.google.android.gms:play-services-ads:22.6.0
android.meta_data = com.google.android.gms.ads.APPLICATION_ID=ca-app-pub-5522917995813710~6900495663

# ---------------------------------------------------------
# EK MANIFEST
# ---------------------------------------------------------
android.extra_manifest_xml = .android/extra_manifest.xml

# ---------------------------------------------------------
# DESTEKLENEN MIMARILER
# ---------------------------------------------------------
android.archs = arm64-v8a, armeabi-v7a

# ---------------------------------------------------------
# LOG
# ---------------------------------------------------------
log_level = 2


[buildozer]

log_level = 2
warn_on_root = 1
