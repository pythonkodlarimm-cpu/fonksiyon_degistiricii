# Genel Bakış

[⬅ Ana Sayfa](../README.md) | [➡ Kullanım Rehberi](usage.md)

---

# Fonksiyon Değiştirici Nedir

Fonksiyon Değiştirici, Python dosyaları içindeki fonksiyonları taramak, seçmek, düzenlemek ve güvenli biçimde güncellemek için geliştirilmiş modüler bir araçtır.

Bu uygulama özellikle şu ihtiyacı çözmek için tasarlanmıştır:

- büyük Python dosyalarında fonksiyonları hızlıca bulmak
- belirli bir fonksiyonu güvenli şekilde güncellemek
- yanlış kod düzenleme riskini azaltmak
- dosya üzerinde kontrollü değişiklik yapmak
- değişiklik öncesi otomatik yedek almak
- gerektiğinde son yedekten geri yüklemek

Uygulama hem masaüstü Python ortamında hem de Android cihazlarda çalışabilecek şekilde tasarlanmıştır.

---

# Projenin Amacı

Bu projenin temel amacı Python dosyaları üzerinde **fonksiyon bazlı düzenleme** yapabilen güvenli bir araç sunmaktır.

Çoğu zaman geliştiriciler:

- büyük Python dosyalarında çalışır
- belirli bir fonksiyonu değiştirmek ister
- yanlışlıkla başka kodları bozma riski yaşar

Fonksiyon Değiştirici bu süreci daha güvenli ve daha kontrollü hale getirir.

Temel yaklaşım:

1. Dosya seç
2. Fonksiyonları tara
3. Fonksiyon seç
4. Kod düzenle
5. Doğrula
6. Güvenli güncelle
7. Yedek oluştur
8. Gerekirse geri yükle

---

# Bu Proje Ne Değildir

Fonksiyon Değiştirici tam kapsamlı bir IDE değildir.

Bu araç aşağıdakilerin yerine geçmez:

- VS Code
- PyCharm
- tam kod editörleri
- proje yönetim araçları

Bunun yerine şu işe odaklanır:

> Python dosyaları içindeki fonksiyonları güvenli biçimde düzenlemek.

Bu odak sayesinde uygulama sade, hızlı ve kontrollü bir kullanım sunar.

---

# Temel Özellikler

Fonksiyon Değiştirici aşağıdaki özellikleri sunar:

## Python Fonksiyon Tarama

Seçilen Python dosyası analiz edilir ve içindeki fonksiyonlar listelenir.

## Fonksiyon Bazlı Seçim

Kullanıcı listedeki fonksiyonlardan birini seçebilir.

## Mevcut Kod Görüntüleme

Seçilen fonksiyonun mevcut hali görüntülenir.

## Yeni Kod Düzenleme

Kullanıcı yeni fonksiyon kodunu yazabilir veya düzenleyebilir.

## Sözdizimi Doğrulama

Kod güncellenmeden önce temel Python sözdizimi kontrolü yapılır.

## Güvenli Güncelleme

Yeni kod doğrudan dosyaya yazılmaz.

Önce güvenli yazma işlemi uygulanır.

## Otomatik Yedekleme

Her güncellemeden önce dosyanın yedeği alınır.

## Geri Yükleme

Gerekirse son yedek kolayca geri yüklenebilir.

## Android Uyumluluğu

Android sistem belge seçici desteği bulunur.

## Modüler Mimari

Uygulama modüler katmanlar kullanılarak geliştirilmiştir.

---

# Nasıl Çalışır

Uygulamanın çalışma mantığı aşağıdaki akışa dayanır.

```
Dosya Seç
   │
   ▼
Fonksiyonları Tara
   │
   ▼
Fonksiyon Seç
   │
   ▼
Mevcut Kodu Gör
   │
   ▼
Yeni Kodu Yaz
   │
   ▼
Kod Doğrulama
   │
   ▼
Güvenli Güncelleme
   │
   ▼
Yedek Oluşturma
   │
   ▼
Gerekirse Geri Yükleme
```

Bu akış hem güvenliği hem de kullanım kolaylığını sağlar.

---

# Kullanım Senaryoları

Fonksiyon Değiştirici özellikle şu durumlarda faydalıdır.

## Büyük Python Dosyaları

Çok sayıda fonksiyon içeren dosyaları düzenlerken.

## Mobil Python Geliştirme

Android cihaz üzerinde Python dosyası düzenlerken.

## Kod Refactor Araçları

Fonksiyon bazlı düzenleme araçları geliştirirken.

## Eğitim Amaçlı Kullanım

Python kod analizi ve AST tabanlı araçlar öğrenirken.

---

# Android Ortamı

Android üzerinde Python dosyaları ile çalışmak masaüstünden farklıdır.

Bu nedenle uygulama şu mekanizmaları kullanır:

- sistem belge seçici
- çalışma kopyası
- güvenli yazma
- dosya erişim kontrolü

Bu yaklaşım Android dosya sistemi ile uyumlu bir çalışma sağlar.

---

# Proje Yapısı

Proje modüler bir yapı kullanır.

```
app
 ├─ core
 ├─ services
 └─ ui

docs
 ├─ overview.md
 ├─ usage.md
 ├─ architecture.md
 └─ security.md
```

Her katman farklı sorumluluklara sahiptir.

---

# Mimari

Uygulama üç ana katmandan oluşur.

1. UI Katmanı
2. Servis Katmanı
3. Core Katmanı

Detaylı mimari açıklaması için:

➡ [Mimari Dokümantasyonu](architecture.md)

---

# Güvenlik Yaklaşımı

Fonksiyon Değiştirici veri güvenliğini önemser.

Bu nedenle şu prensipleri kullanır:

- çalışma kopyası oluşturma
- otomatik yedekleme
- güvenli yazma
- atomik replace
- geri yükleme mekanizması

Detaylı bilgi:

➡ [Güvenlik Dokümantasyonu](security.md)

---

# Sonuç

Fonksiyon Değiştirici, Python dosyaları üzerinde güvenli ve kontrollü değişiklik yapılmasını sağlayan modüler bir araçtır.

Bu proje:

- fonksiyon bazlı düzenleme sunar
- güvenli yazma mekanizması kullanır
- yedekleme ve geri yükleme sağlar
- Android ve masaüstü ortamlarını destekler
- modüler mimari kullanır

Bu sayede hem geliştiriciler hem de araç geliştiricileri için güçlü bir temel sunar.

---

[➡ Kullanım Rehberi](usage.md)
