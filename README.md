# JS Destekli Genel Zafiyet Crawler 🕷

Bu proje, **Playwright** ve **BeautifulSoup** kullanarak çalışan, **JS destekli web crawler** içerir.  
Amaç, bir veya birden fazla URL üzerinden:

- **Parametreli GET URL'leri** toplamak (genel zafiyet adayı olarak)
- Sayfa içindeki **POST formlarını tespit edip POST endpoint’lerini** listelemek
- **Dizin (directory) URL’lerini** çıkarmak
- Tüm bunları hem detaylı rapor hem de sade URL listesi olarak kaydetmek

> ⚠ Oluşacak zararlı olaylardan **geliştirici sorumlu değildir**. Kapsam içerisinde veya laboratuvar ortamlarında **LEGAL KALIN!**  

---

## 🧩 Gereksinimler

- Python 3.8+
- Playwright
- BeautifulSoup4

---

## 🚀 Özellikler

- **JavaScript destekli tarama**  
  Playwright ile sayfalar JS render edildikten sonra taranır. Bu sayede:
  - SPA yapıları
  - Dinamik menüler
  - JS ile üretilen linkler  
  gibi klasik `requests` tabanlı tarayıcıların kaçırdığı URL'ler de yakalanabilir.

- **GET Parametreli URL Tespiti**  
  İçinde `?` ve `=` geçen URL'ler **"genel zafiyet adayı"** olarak işaretlenir.  
  Örnek:
  - `https://site.com/page.php?id=1`
  - `https://site.com/search?q=test&page=2`

- **POST Endpoint Tespiti**  
  Sayfadaki `<form>` etiketleri parse edilir:
  - `method="post"` olan formlar bulunur
  - `action` değeri tam URL’ye dönüştürülür
  - Bu URL’ler **POST endpoint listesi**ne eklenir

- **Dizin (Directory) Keşfi**  
  Sonu `/` ile biten ve ilgili başlangıç scope’u içinde kalan URL'ler dizin olarak işaretlenir:
  - `https://site.com/admin/`
  - `https://site.com/users/`

- **Scope Sınırı (Sadece İlgili Dizin ve Altı)**  
  Her başlangıç URL için crawler:
  - Sadece **aynı dizin ve altındaki** URL’leri tarar  
    Örneğin:
    - `https://site.com/app/login.php` için scope:
      - `https://site.com/app/` altındaki tüm URL’ler

- **Çift Çıkış Sistemi**
  - `results.txt` → Detaylı rapor
  - `urls_only.txt` → Tek satırda 1 URL olacak şekilde sade liste (tekrarsız)

---

## 📂 Proje Yapısı

Örnek minimal repo yapısı:

```text
.
├── crawler.py        # JS destekli genel zafiyet crawler
├── urls.txt          # Başlangıç URL'leri (kullanıcı tarafından oluşturulur)
└── README.md
```
---
