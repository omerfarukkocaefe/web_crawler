# js_crawler.py
#
# Playwright tabanlı Genel Zafiyet Crawler
# - JS çalıştırır (dinamik linkleri görür)
# - GET parametreli URL'leri toplar (genel zafiyet adayı)
# - POST formlarını bulur (POST endpoint'leri listeler)
# - Dizinleri toplar
# - Çıktı:
#     results.txt   -> detaylı rapor
#     urls_only.txt -> sadece URL listesi (alt alta, tekrarsız)
#
# Kullanım:
#   1) urls.txt dosyasına her satıra bir URL yaz
#   2) python crawler.py

import time
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def normalize_url(url: str) -> str:
    """
    URL'den fragment (#...) kısmını atar, boşlukları kırpar.
    """
    if not url:
        return ""
    url = url.strip()
    if "#" in url:
        url = url.split("#", 1)[0]
    return url


def crawl_for_vulns_js(start_url, page, max_pages=30, wait_time=3):
    """
    Tek bir başlangıç URL'i için JS destekli crawl yapar.
    - page: Playwright Page objesi (önceden oluşturulmuş olmalı)
    - max_pages: Bu başlangıç için maksimum sayfa sayısı
    - wait_time: Her sayfa sonrası JS yüklenmesi için bekleme süresi (saniye)
    """

    start_url = normalize_url(start_url)
    if not start_url:
        return [], [], [], []

    parsed = urlparse(start_url)
    base_prefix = f"{parsed.scheme}://{parsed.netloc}"

    # Sadece ilgili dizin + altındakiler
    if start_url.endswith("/"):
        scope_prefix = start_url
    else:
        scope_prefix = start_url.rsplit("/", 1)[0] + "/"

    visited = set()
    queue = [start_url]

    vuln_candidates = set()   # Parametreli GET URL'ler (genel zafiyet adayı)
    directories = set()       # Dizin URL'ler
    found_urls = set()        # Bu başlangıç için görülen TÜM URL'ler
    post_endpoints = set()    # POST endpoint URL'ler

    page_count = 0

    while queue and page_count < max_pages:
        current_url = queue.pop(0)
        current_url = normalize_url(current_url)

        if not current_url or current_url in visited:
            continue

        print(f"[{page_count + 1}] Ziyaret ediliyor: {current_url}")
        found_urls.add(current_url)

        try:
            # JS destekli ziyaret
            page.goto(current_url, wait_until="domcontentloaded", timeout=20000)
        except Exception as e:
            print(f"⚠ Sayfa yükleme hatası: {current_url} -> {e}")
            visited.add(current_url)
            continue

        # Biraz bekleyip (JS çalışsın) HTML içeriğini alalım
        time.sleep(wait_time)

        final_url = normalize_url(page.url)
        if final_url and final_url != current_url:
            # Redirect vb. varsa final URL'i de kaydedelim
            found_urls.add(final_url)
            current_url = final_url

        try:
            html = page.content()
        except Exception as e:
            print(f"⚠ İçerik alınamadı: {current_url} -> {e}")
            visited.add(current_url)
            continue

        soup = BeautifulSoup(html, "html.parser")

        # -----------------------------------------------
        # 1) POST form yakalama (GENEL ZAFİYET ADAYI)
        # -----------------------------------------------
        for form in soup.find_all("form"):
            action = form.get("action", "")
            method = form.get("method", "get").lower().strip()

            full_url = urljoin(current_url, action) if action else current_url
            full_url = normalize_url(full_url)

            if method == "post":
                print(f"📨 POST endpoint bulundu: {full_url}")
                post_endpoints.add(full_url)

        # -----------------------------------------------
        # 2) Parametreli GET URL → genel zafiyet adayı
        # -----------------------------------------------
        if "?" in current_url and "=" in current_url:
            vuln_candidates.add(current_url)
            print(f"🔍 Parametreli URL (zafiyet adayı) bulundu: {current_url}")

        # -----------------------------------------------
        # 3) Dizin gibi görünen URL
        # -----------------------------------------------
        elif current_url.endswith("/") and current_url.startswith(scope_prefix):
            directories.add(current_url)
            print(f"📁 Dizin bulundu: {current_url}")

        # -----------------------------------------------
        # 4) Sayfadaki linkleri sıraya ekle (JS sonrası DOM)
        # -----------------------------------------------
        for link in soup.find_all("a"):
            href = link.get("href")
            if not href:
                continue

            full_url = urljoin(current_url, href)
            full_url = normalize_url(full_url)

            # 2) Sadece ilgili dizin ve altı (scope_prefix)
            if full_url.startswith(scope_prefix) and full_url not in visited:
                queue.append(full_url)

            #if full_url.startswith(base_prefix) and full_url.startswith(scope_prefix) and full_url not in visited:
            #    queue.append(full_url)


        visited.add(current_url)
        page_count += 1

    return list(vuln_candidates), list(directories), list(found_urls), list(post_endpoints)


def main():
    print("🔎 JS Destekli Genel Zafiyet Crawler Başlatılıyor...")

    # URL'leri dosyadan oku
    try:
        with open("urls.txt", "r", encoding="utf-8") as f:
            initial_urls = [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print("❌ urls.txt bulunamadı! Aynı dizinde urls.txt oluşturup içine URL'leri ekle.")
        return

    if not initial_urls:
        print("❌ urls.txt dosyasında hiç URL yok!")
        return

    # Taranacak başlangıç URL set'i ve işlenmiş start'lar
    to_crawl = set(initial_urls)
    processed_starts = set()

    # Aynı URL'in urls_only.txt'ye birden fazla yazılmaması için global set
    written_urls = set()

    # Çıktı dosyalarını temizle
    open("results.txt", "w").close()
    open("urls_only.txt", "w").close()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        while to_crawl:
            start_url = to_crawl.pop()
            start_url = normalize_url(start_url)

            if not start_url or start_url in processed_starts:
                continue

            print(f"\n🕷 Yeni başlangıç dizini taranıyor: {start_url}\n")
            vuln_candidates, dirs, found_urls, post_urls = crawl_for_vulns_js(
                start_url, page, max_pages=30, wait_time=3
            )

            # Yeni bulunan dizinleri tekrar taranacak listeye ekle
            for d in dirs:
                d = normalize_url(d)
                if d and d not in processed_starts:
                    to_crawl.add(d)

            processed_starts.add(start_url)

            # ---------------------------------------------------
            # 1) DETAYLI RAPORU results.txt'ye yaz
            # ---------------------------------------------------
            with open("results.txt", "a", encoding="utf-8") as f:
                f.write(f"\n=== 📁 Taranan başlangıç dizini: {start_url} ===\n")

                # Dizindeki tüm URL'ler
                f.write("\n--- İçerik URL'leri ---\n")
                for u in sorted(set(map(normalize_url, found_urls))):
                    if u:
                        f.write(u + "\n")

                # Genel zafiyet adayı URL'ler (Parametreli GET)
                f.write("\n--- Genel Zafiyet Adayı URL'ler (Parametreli GET) ---\n")
                for v in sorted(set(map(normalize_url, vuln_candidates))):
                    if v:
                        f.write(v + "\n")

                # POST endpoint'ler
                f.write("\n--- POST Endpoint'leri ---\n")
                for purl in sorted(set(map(normalize_url, post_urls))):
                    if purl:
                        f.write("POST " + purl + "\n")

                # Bulunan dizinler
                f.write("\n--- Bulunan Dizinler ---\n")
                for d in sorted(set(map(normalize_url, dirs))):
                    if d:
                        f.write(d + "\n")

            # ---------------------------------------------------
            # 2) SADECE URL LİSTESİNİ urls_only.txt'ye ekle
            #    (tek satır = tek URL, hiçbir başlık yok)
            # ---------------------------------------------------
            with open("urls_only.txt", "a", encoding="utf-8") as f:
                # İçerik URL'leri
                for u in found_urls:
                    u = normalize_url(u)
                    if u and u not in written_urls:
                        f.write(u + "\n")
                        written_urls.add(u)

                # GET zafiyet adayları
                for v in vuln_candidates:
                    v = normalize_url(v)
                    if v and v not in written_urls:
                        f.write(v + "\n")
                        written_urls.add(v)

                # POST endpoint'ler
                for purl in post_urls:
                    purl = normalize_url(purl)
                    if purl and purl not in written_urls:
                        f.write(purl + "\n")
                        written_urls.add(purl)

                # Dizinler
                for d in dirs:
                    d = normalize_url(d)
                    if d and d not in written_urls:
                        f.write(d + "\n")
                        written_urls.add(d)

        browser.close()

    print("\n✅ Tarama tamamlandı!")
    print("➡ Detaylı rapor: results.txt")
    print("➡ Sadece URL listesi: urls_only.txt")


if __name__ == "__main__":
    main()
