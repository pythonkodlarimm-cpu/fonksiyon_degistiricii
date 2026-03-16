# Güvenlik

[⬅ Mimari](architecture.md) | [⬅ Ana Sayfa](../README.md)

---

# Güvenlik Yaklaşımı

Fonksiyon Değiştirici uygulaması Python dosyalarını düzenlerken veri bütünlüğünü korumayı hedefler.

Kod dosyaları doğrudan değiştirilirse:

- veri kaybı yaşanabilir
- dosya bozulabilir
- yarım yazma gerçekleşebilir
- yanlış fonksiyon düzenlenebilir

Bu nedenle uygulama **güvenli yazma ve yedekleme prensipleri** kullanır.

Temel hedefler:

- veri kaybını önlemek
- kod bütünlüğünü korumak
- geri dönüş imkanı sağlamak
- güvenli dosya güncelleme yapmak

---

# Güvenlik Prensipleri

Uygulama şu prensiplere dayanır.

## Kontrollü Dosya Erişimi

Dosyalar doğrudan rastgele erişilmez.

Her işlem:

- doğrulanmış dosya yolu
- çalışma oturumu
- kontrollü okuma

ile gerçekleştirilir.

---

## Çalışma Kopyası Kullanımı

Seçilen dosya doğrudan değiştirilmez.

Önce bir **çalışma kopyası** oluşturulur.

Bu yöntem:

- orijinal dosyanın korunmasını sağlar
- test işlemlerinin güvenli yapılmasına izin verir
- hatalı yazma riskini azaltır

---

## Otomatik Yedekleme

Her güncellemeden önce dosyanın bir yedeği oluşturulur.

Yedek dosyası şu durumlarda kullanılır:

- güncelleme başarısız olursa
- kullanıcı geri yükleme yapmak isterse
- kod beklenmeyen şekilde bozulursa

---

## Atomik Yazma

Dosyaya yeni içerik doğrudan yazılmaz.

Uygulanan yöntem:

1. yeni içerik geçici dosyaya yazılır  
2. disk senkronizasyonu yapılır  
3. dosya atomik replace ile değiştirilir  

Bu yaklaşım şu riskleri azaltır:

- yarım yazma
- bozuk dosya oluşması
- veri kaybı

---

# Güncelleme Akışı

Fonksiyon güncelleme işlemi aşağıdaki adımlarla gerçekleşir.

```
1 Dosya okunur
2 Yedek oluşturulur
3 Yeni kod doğrulanır
4 Güncellenmiş içerik hazırlanır
5 Geçici dosya oluşturulur
6 Yeni içerik yazılır
7 Atomik replace uygulanır
```

Bu süreç veri güvenliğini artırır.

---

# Sözdizimi Doğrulama

Yeni fonksiyon kodu yazıldıktan sonra temel doğrulama yapılır.

Kontrol edilen noktalar:

- kodun tek bir fonksiyon içermesi
- Python sözdizimi hatası olmaması
- fonksiyon tanımının doğru başlaması

Bu doğrulama hatalı kod yazılmasını engeller.

---

# Yanlış Fonksiyon Güncellemesini Önleme

Fonksiyon güncellemesi yapılırken:

- fonksiyon yolu
- fonksiyon adı
- satır konumu

gibi bilgiler doğrulanır.

Bu sayede yanlış fonksiyonun güncellenmesi engellenir.

---

# Geri Yükleme Mekanizması

Eğer bir güncelleme sorun yaratırsa kullanıcı son yedeği geri yükleyebilir.

Geri yükleme süreci:

1. son yedek bulunur  
2. yedek dosya doğrulanır  
3. mevcut dosya yerine yazılır  

Bu özellik kod güvenliğini artırır.

---

# Android Güvenlik Notları

Android ortamında dosya erişimi masaüstünden farklıdır.

Bu nedenle uygulama şu mekanizmaları kullanır:

- sistem belge seçici
- çalışma kopyası
- dosya erişim kontrolü

Bu yaklaşım Android dosya sistemi ile uyumludur.

---

# Kullanıcı Sorumluluğu

Uygulama güvenli yazma mekanizmaları kullanmasına rağmen kullanıcıların da dikkatli olması gerekir.

Öneriler:

- önemli projelerde ek yedek almak
- kodu güncellemeden önce kontrol etmek
- büyük değişikliklerde versiyon kontrol kullanmak

---

# Güvenlik Sınırları

Bu uygulama aşağıdaki konular için tasarlanmamıştır:

- kötü amaçlı yazılım analizi
- güvenlik açıkları tespiti
- sandbox koruması
- kod imzalama

Uygulamanın amacı **güvenli kod düzenleme süreci sağlamaktır.**

---

# Veri Gizliliği

Fonksiyon Değiştirici:

- internet bağlantısı kullanmaz
- veri toplamaz
- kullanıcı dosyalarını dışarı göndermez

Tüm işlemler yerel cihaz üzerinde gerçekleştirilir.

---

# Özet

Fonksiyon Değiştirici aşağıdaki güvenlik mekanizmalarını kullanır:

- çalışma kopyası
- otomatik yedekleme
- sözdizimi doğrulama
- atomik dosya yazma
- geri yükleme sistemi

Bu yaklaşım Python dosyalarının güvenli biçimde düzenlenmesini sağlar.

---

[⬅ Mimari](architecture.md) | [⬅ Ana Sayfa](../README.md)