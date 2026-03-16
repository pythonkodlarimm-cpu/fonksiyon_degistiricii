# Mimari

[⬅ Kullanım Rehberi](usage.md) | [⬅ Ana Sayfa](../README.md)

---

# Genel Mimari

Fonksiyon Değiştirici uygulaması **modüler mimari** kullanılarak geliştirilmiştir.

Bu mimarinin amacı:

- kodun okunabilirliğini artırmak
- test edilebilirliği kolaylaştırmak
- UI ve iş mantığını ayırmak
- projeyi büyütmeyi kolaylaştırmak
- yeni özellik eklemeyi basitleştirmek

Uygulama üç ana katmandan oluşur:

1. UI Katmanı  
2. Servis Katmanı  
3. Core Katmanı  

Bu katmanlar birbirinden bağımsız çalışacak şekilde tasarlanmıştır.

---

# Mimari Katmanlar

## 1. UI Katmanı

```
app/ui
```

Bu katman kullanıcı arayüzünü içerir.

Görevleri:

- ekranları oluşturmak
- kullanıcı etkileşimini almak
- servisleri tetiklemek
- sonuçları kullanıcıya göstermek

UI katmanı **iş mantığı içermez**.

UI sadece servisleri çağırır.

Örnek dosyalar:

```
root.py
dosya_secici.py
fonksiyon_listesi.py
editor_paneli.py
durum_cubugu.py
gecici_bildirim.py
```

### Root Widget

```
app/ui/root.py
```

Uygulamanın ana kontrol noktasıdır.

Görevleri:

- ekran bileşenlerini bağlamak
- servisleri çağırmak
- uygulama akışını yönetmek
- durum mesajlarını göstermek

Root widget çizim yapmaz.

---

### Dosya Seçici

```
app/ui/dosya_secici.py
```

Görevleri:

- kullanıcıdan Python dosyası seçmek
- belge oturumu başlatmak
- fonksiyon tarama işlemini tetiklemek

---

### Fonksiyon Listesi

```
app/ui/fonksiyon_listesi.py
```

Görevleri:

- taranan fonksiyonları listelemek
- kullanıcıya seçim imkanı sunmak
- seçilen fonksiyonu editör paneline iletmek

---

### Editör Paneli

```
app/ui/editor_paneli.py
```

Görevleri:

- mevcut fonksiyon kodunu göstermek
- yeni fonksiyon kodunu düzenletmek
- doğrulama yapmak
- güncelleme ve geri yükleme işlemlerini başlatmak

---

### Durum Çubuğu

```
app/ui/durum_cubugu.py
```

Görevleri:

- kısa bilgi mesajları göstermek
- hata veya başarı durumlarını bildirmek

---

### Geçici Bildirim

```
app/ui/gecici_bildirim.py
```

Görevleri:

- kısa süreli işlem bildirimleri göstermek

Örnek:

- kopyalandı
- güncellendi
- doğrulandı

---

# 2. Servis Katmanı

```
app/services
```

Bu katman uygulamanın **iş mantığını** içerir.

Servislerin amacı:

- UI'dan bağımsız çalışmak
- tekrar kullanılabilir olmak
- test edilebilir olmak

Servisler UI bileşenlerini bilmez.

UI servisleri çağırır.

---

### Dosya Servisi

```
dosya_servisi.py
```

Görevleri:

- dosya okuma
- dosya yazma
- dosya varlık kontrolü

---

### Belge Oturumu Servisi

```
belge_oturumu_servisi.py
```

Görevleri:

- belge seçildiğinde çalışma oturumu başlatmak
- çalışma kopyası oluşturmak
- dosya yollarını yönetmek

---

### Geri Yükleme Servisi

```
belge_geri_yukleme_servisi.py
```

Görevleri:

- son yedekten geri yükleme yapmak
- yedek dosyaları yönetmek

---

### Geçici Bildirim Servisi

```
gecici_bildirim_servisi.py
```

Görevleri:

- UI üzerinde toast / bildirim göstermek
- işlem geri bildirimleri üretmek

---

# 3. Core Katmanı

```
app/core
```

Bu katman **algoritmik işlemleri** içerir.

Core katmanı UI veya servis bağımlılığı içermez.

---

### Fonksiyon Tarayıcı

```
tarayici.py
```

Görevleri:

- Python dosyasını analiz etmek
- fonksiyonları tespit etmek
- fonksiyon listesi oluşturmak

---

### Fonksiyon Değiştirici

```
degistirici.py
```

Görevleri:

- seçilen fonksiyonun yerini bulmak
- yeni kodu doğru yere yerleştirmek
- güncellenmiş kaynak kod üretmek

---

# Veri Akışı

Uygulama şu veri akışıyla çalışır.

```
Kullanıcı
   │
   ▼
UI Katmanı
   │
   ▼
Servis Katmanı
   │
   ▼
Core Katmanı
   │
   ▼
Dosya Güncelleme
```

Adım adım:

1. kullanıcı dosya seçer  
2. UI servis çağırır  
3. servis çalışma kopyası oluşturur  
4. core fonksiyonları tarar  
5. kullanıcı fonksiyon seçer  
6. yeni kod yazılır  
7. doğrulama yapılır  
8. core kodu günceller  
9. servis güvenli şekilde dosyaya yazar  

---

# Güvenli Yazma Akışı

Dosyalar doğrudan üzerine yazılmaz.

Uygulanan yöntem:

1. mevcut dosya okunur  
2. yedek oluşturulur  
3. yeni içerik geçici dosyaya yazılır  
4. fsync uygulanır  
5. atomik replace yapılır  

Bu sayede:

- veri kaybı riski azalır
- bozuk yazma önlenir
- geri yükleme mümkün olur

---

# Modüler Tasarımın Avantajları

Bu mimari şu avantajları sağlar:

- kod daha okunabilir
- hata ayıklama kolaylaşır
- servisler yeniden kullanılabilir
- UI bağımlılığı azalır
- test yazmak kolaylaşır
- yeni özellik eklemek kolaylaşır

---

# Genişletilebilirlik

Bu mimari gelecekte şu özellikleri eklemeyi kolaylaştırır:

- diff karşılaştırma ekranı
- çoklu yedek geçmişi
- plugin sistemi
- otomatik kod analiz araçları
- sınıf / method tarama geliştirmeleri
- gelişmiş AST doğrulama

---

# Sonuç

Fonksiyon Değiştirici uygulaması:

- modüler
- servis tabanlı
- güvenli yazma prensipleri kullanan
- genişletilebilir

bir mimari üzerine kurulmuştur.

Bu yapı hem masaüstü hem Android ortamında
kararlı şekilde çalışacak şekilde tasarlanmıştır.

---

[⬅ Kullanım Rehberi](usage.md) | [⬅ Ana Sayfa](../README.md)
