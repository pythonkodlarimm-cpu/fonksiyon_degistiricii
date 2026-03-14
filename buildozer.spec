[app]
title = Fonksiyon Degistirici
package.name = fonksiyondegistirici
package.domain = org.carprazz

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,json,ttf,atlas,txt

version = 0.1.0

requirements = python3,kivy

orientation = portrait
fullscreen = 0

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

android.minapi = 21
android.api = 31
android.sdk = 31
android.archs = arm64-v8a, armeabi-v7a

android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
