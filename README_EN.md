# JS-Powered General Vulnerability Crawler 🕷

This project includes a **JavaScript-enabled web crawler** built with **Playwright** and **BeautifulSoup**.  
Its purpose is to scan one or multiple URLs and extract:

- **Parameterized GET URLs** (potential vulnerability candidates)
- **POST forms** and corresponding **POST endpoints**
- **Directory-style URLs**
- All collected data into both a detailed report and a clean URL list

> ⚠ The developer is **NOT responsible** for any harmful or illegal misuse.  
> Always stay **LEGAL** and operate **within authorized scope or lab environments**.

---

## 🧩 Requirements

- Python 3.8+
- Playwright
- BeautifulSoup4

---
## 🧩 Usage

```
python .\crawler.py
```

---

## 🚀 Features

- **JavaScript-Aware Crawling**  
  Thanks to Playwright, pages are scanned *after* JS rendering. This allows detection of:
  - SPA structures
  - Dynamic menus
  - JS-generated links  
  All of which traditional `requests`-based crawlers typically miss.

- **GET Parameter Detection**  
  URLs containing `?` and `=` are flagged as **“general vulnerability candidates.”**  
  Examples:
  - `https://site.com/page.php?id=1`
  - `https://site.com/search?q=test&page=2`

- **POST Endpoint Detection**  
  The crawler analyzes `<form>` elements:
  - Detects forms using `method="post"`
  - Converts the form `action` to a full URL
  - Stores each URL as a **POST endpoint**

- **Directory Discovery**  
  URLs ending with `/` and within the current scope are marked as directories:
  - `https://site.com/admin/`
  - `https://site.com/users/`

- **Scope Restriction (Only the Target Directory and Below)**  
  For each starting URL, the crawler only scans **the same directory and its subpaths**.  
  Example:
  - Starting URL: `https://site.com/app/login.php`  
    → Scope: everything under  
      `https://site.com/app/`

- **Dual Output System**
  - `results.txt` → Detailed structured crawl report  
  - `urls_only.txt` → One URL per line, clean and deduplicated

---

## 📂 Project Structure

Example minimal repository layout:

```text
.
├── crawler.py        # JS-enabled general vulnerability crawler
├── urls.txt          # Starting URLs (provided by the user)
└── README.md
