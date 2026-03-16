# Kullanım Rehberi

[⬅ Genel Bakış](overview.md) | [➡ Mimari](architecture.md) | [⬅ Ana Sayfa](../README.md)

---

# Giriş

Bu doküman Fonksiyon Değiştirici uygulamasının nasıl kullanılacağını adım adım açıklar.

Uygulama Python dosyaları içindeki fonksiyonları:

- taramak
- seçmek
- düzenlemek
- doğrulamak
- güvenli şekilde güncellemek
- yedekten geri yüklemek

için tasarlanmıştır.

---

# Kullanım Akışı

Uygulamanın temel kullanım akışı aşağıdaki gibidir.

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
Mevcut Kodu İncele
   │
   ▼
Yeni Kod Yaz
   │
   ▼
Kod Doğrulama
   │
   ▼
Güncelle
   │
   ▼
Gerekirse Geri Yükle
```

Bu akış güvenli kod düzenleme sağlar.

---

# 1. Dosya Seçme

İlk adım düzenlemek istediğiniz Python dosyasını seçmektir.

Dosya seçici şu görevleri yerine getirir:

- Python dosyasını seçmek
- dosya yolunu doğrulamak
- belge oturumu başlatmak
- çalışma kopyası oluşturmak

Android ortamında sistem belge seçici kullanılabilir.

Bu sayede dosya erişimi güvenli şekilde sağlanır.

---

# 2. Fonksiyon Tarama

Dosya seçildikten sonra uygulama dosyayı analiz eder.

Bu işlem sırasında:

- Python dosyası okunur
- AST analizi yapılır
- fonksiyon tanımları bulunur
- fonksiyon listesi oluşturulur

Tarama sonucunda kullanıcıya bir fonksiyon listesi gösterilir.

---

# 3. Fonksiyon Seçme

Kullanıcı fonksiyon listesinden bir fonksiyon seçer.

Seçim yapıldığında:

- fonksiyon yolu belirlenir
- fonksiyon içeriği okunur
- editör paneline aktarılır

Bu aşamada kullanıcı mevcut kodu görüntüleyebilir.

---

# 4. Mevcut Kodu İnceleme

Editör panelinde seçilen fonksiyonun mevcut kodu gösterilir.

Bu alan:

- sadece okunabilir
- değiştirilemez
- referans amaçlıdır

Kullanıcı mevcut kodu inceleyebilir ve yeni kodu buna göre yazabilir.

---

# 5. Yeni Fonksiyon Kodu Yazma

Yeni fonksiyon kodu editör alanına yazılır.

Bu alanda kullanıcı:

- fonksiyon kodunu yeniden yazabilir
- mevcut kodu kopyalayabilir
- düzenleme yapabilir

Yeni kod tam bir Python fonksiyonu olmalıdır.

Örnek:

```
def example_function(x):
    return x * 2
```

---

# 6. Kod Doğrulama

Kod güncellenmeden önce doğrulama yapılır.

Kontrol edilen noktalar:

- kod boş mu
- kod tek bir fonksiyon mu
- Python sözdizimi doğru mu
- fonksiyon tanımı doğru mu

Hatalar kullanıcıya gösterilir.

---

# 7. Güncelleme

Kod doğrulama başarılıysa güncelleme yapılabilir.

Güncelleme işlemi sırasında:

1. mevcut dosya okunur  
2. yedek oluşturulur  
3. yeni fonksiyon kodu hazırlanır  
4. güncellenmiş içerik oluşturulur  
5. dosya güvenli şekilde yazılır  

Bu işlem dosya bütünlüğünü korur.

---

# 8. Yedekleme

Her güncellemeden önce otomatik yedek alınır.

Yedek dosyası:

- güncelleme hatası durumunda
- yanlış kod yazıldığında
- geri dönüş gerektiğinde

kullanılabilir.

---

# 9. Geri Yükleme

Geri yükleme özelliği son yedeği tekrar uygulamanızı sağlar.

Bu işlem:

1. yedek dosyayı bulur  
2. yedek içeriği doğrular  
3. mevcut dosyanın yerine yazar  

Bu sayede kod eski haline döner.

---

# 10. Geçici Bildirimler

Uygulama kullanıcıya kısa bildirimler gösterir.

Örnek bildirimler:

- kod kopyalandı
- kod doğrulandı
- güncelleme başarılı
- hata oluştu
- geri yükleme tamamlandı

Bu bildirimler kısa süreli görünür.

---

# Android Kullanımı

Android cihazlarda dosya erişimi farklıdır.

Bu nedenle uygulama:

- sistem belge seçici
- çalışma kopyası
- güvenli yazma

mekanizmalarını kullanır.

Android kullanıcıları için öneriler:

- dosya izinlerini kontrol edin
- belge seçiciyi kullanın
- önemli dosyaların yedeğini alın

---

# İpuçları

Daha güvenli kullanım için şu öneriler uygulanabilir.

## Küçük Değişiklikler Yapın

Büyük değişiklikler yerine küçük güncellemeler yapmak daha güvenlidir.

## Kod Doğrulamasını Kullanın

Güncellemeden önce doğrulama yapmak hataları azaltır.

## Yedekleri Saklayın

Yedek dosyaları saklamak geri dönüş için faydalıdır.

## Versiyon Kontrol Kullanın

Git gibi versiyon kontrol sistemleri ile birlikte kullanmak önerilir.

---

# Yaygın Hatalar

## Fonksiyon Tanımı Eksik

Yanlış:

```
return x * 2
```

Doğru:

```
def example(x):
    return x * 2
```

---

## Birden Fazla Fonksiyon

Yeni kod alanı yalnızca **tek fonksiyon** içermelidir.

---

# Sonuç

Fonksiyon Değiştirici uygulaması Python fonksiyonlarını düzenlemek için güvenli bir akış sunar.

Temel avantajları:

- fonksiyon bazlı düzenleme
- güvenli güncelleme
- otomatik yedekleme
- geri yükleme
- Android uyumluluğu

Bu özellikler sayesinde Python dosyalarını düzenlemek daha güvenli hale gelir.

---

[⬅ Genel Bakış](overview.md) | [➡ Mimari](architecture.md)