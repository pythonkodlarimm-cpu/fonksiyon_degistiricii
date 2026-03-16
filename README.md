<p align="center">
  <img src="https://raw.githubusercontent.com/pythonkodlarimm-cpu/fonksiyon_degistiricii/main/docs/banner.png" width="100%">
</p>

<h1 align="center">Fonksiyon Değiştirici</h1>

<p align="center">
Python fonksiyonlarını güvenli biçimde tarayan, düzenleyen, güncelleyen ve yedekten geri yükleyen modüler Kivy aracı
</p>

<p align="center">

<img src="https://img.shields.io/github/stars/pythonkodlarimm-cpu/fonksiyon_degistiricii?style=for-the-badge&logo=github">
<img src="https://img.shields.io/github/forks/pythonkodlarimm-cpu/fonksiyon_degistiricii?style=for-the-badge&logo=github">
<img src="https://img.shields.io/github/watchers/pythonkodlarimm-cpu/fonksiyon_degistiricii?style=for-the-badge&logo=github">
<img src="https://img.shields.io/github/license/pythonkodlarimm-cpu/fonksiyon_degistiricii?style=for-the-badge">
<img src="https://img.shields.io/github/v/release/pythonkodlarimm-cpu/fonksiyon_degistiricii?style=for-the-badge">

</p>

<p align="center">

<img src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white">
<img src="https://img.shields.io/badge/Kivy-2.x-1D9A6C?style=for-the-badge">
<img src="https://img.shields.io/badge/Platform-Android%20%7C%20Desktop-2F80ED?style=for-the-badge">
<img src="https://img.shields.io/badge/Architecture-Modular-F2994A?style=for-the-badge">
<img src="https://img.shields.io/badge/Status-Active-27AE60?style=for-the-badge">

</p>

---

<p align="center">
<b>Seç • Tara • Düzenle • Doğrula • Güncelle • Geri Yükle</b>
</p>

---

# Demo

<p align="center">
  <img src="https://raw.githubusercontent.com/pythonkodlarimm-cpu/fonksiyon_degistiricii/main/docs/demo.gif" width="90%">
</p>

---

# İçindekiler

- [Genel Bakış](docs/overview.md)
- [Kullanım Rehberi](docs/usage.md)
- [Mimari](docs/architecture.md)
- [Güvenlik](docs/security.md)
- [Gizlilik Politikası](docs/privacy-policy.html)

---

# Proje Özeti

**Fonksiyon Değiştirici**, Python dosyaları içerisindeki fonksiyonları analiz eden ve güvenli şekilde güncelleyebilen modüler bir geliştirme aracıdır.

Bu araç bir **tam IDE değildir**.  
Bunun yerine **fonksiyon seviyesinde düzenleme** üzerine odaklanır.

Sağladığı temel özellikler:

- Python dosyası içindeki fonksiyonları otomatik tarama  
- Fonksiyon bazlı düzenleme  
- Güvenli güncelleme mekanizması  
- Otomatik yedek oluşturma  
- Tek tıklamayla geri yükleme  
- Mobil uyumlu arayüz

Bu mimari özellikle **Android üzerinde Python kodu düzenlemek** için tasarlanmıştır.

---

# Kurulum

Gerekli paketleri yükleyin:

```bash
pip install kivy pygments
```

---

# Çalıştırma

Projeyi çalıştırmak için:

```bash
python main.py
```

---

# Repo Yapısı

```
app
├─ core
├─ services
└─ ui

docs
├─ architecture.md
├─ banner.png
├─ demo.gif
├─ index.html
├─ overview.md
├─ privacy-policy.html
├─ security.md
└─ usage.md

android
└─ src
    └─ org
        └─ fy
            └─ bridge
                ├─ AdMobBridge.java
                └─ BillingBridge.java
```

---

# Developer Website

Proje için GitHub Pages üzerinden yayınlanan geliştirici sayfası:

https://pythonkodlarimm-cpu.github.io/fonksiyon_degistiricii/

Bu sayfa şunları içerir:

- uygulama tanıtımı  
- teknik mimari özeti  
- geliştirici bilgileri  
- gizlilik politikası

---

# Gizlilik Politikası

Uygulamanın gizlilik politikası:

https://pythonkodlarimm-cpu.github.io/fonksiyon_degistiricii/privacy-policy.html

---

# Lisans

Bu proje **MIT lisansı** altında dağıtılmaktadır.
