#!/usr/bin/env python3
"""
Scraper para identificar conteúdo mais relevante em https://www.durex.es/
Gera um CSV com as páginas mais ricas em conteúdo (score por tamanho e headings).
"""

import argparse
import csv
import re
import time
from collections import deque
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup


SKIP_EXTENSIONS = {
    ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg",
    ".zip", ".rar", ".7z", ".mp4", ".webm", ".mp3", ".avi",
    ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
}


def normalize_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text


def clean_url(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return ""
    if parsed.scheme not in ("http", "https"):
        return ""
    if any(parsed.path.lower().endswith(ext) for ext in SKIP_EXTENSIONS):
        return ""
    return parsed._replace(fragment="").geturl()


def same_domain(url: str, base_domain: str) -> bool:
    netloc = urlparse(url).netloc.lower()
    return netloc == base_domain or netloc.endswith("." + base_domain)


def build_robot_parser(base_url: str) -> RobotFileParser:
    parsed = urlparse(base_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        return rp
    except Exception:
        return rp


def extract_content(soup: BeautifulSoup) -> dict:
    # Remover elementos não relevantes
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
        tag.decompose()

    title = normalize_text(soup.title.get_text()) if soup.title else ""

    meta_desc = ""
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        meta_desc = normalize_text(meta.get("content"))
    else:
        og = soup.find("meta", attrs={"property": "og:description"})
        if og and og.get("content"):
            meta_desc = normalize_text(og.get("content"))

    h1 = ""
    h1_tag = soup.find("h1")
    if h1_tag:
        h1 = normalize_text(h1_tag.get_text())

    # Preferir conteúdo dentro de <main> ou <article>
    main = soup.find("main") or soup.find("article") or soup.body
    content_text = normalize_text(main.get_text(" ")) if main else ""

    h_count = len(soup.find_all(["h1", "h2", "h3"]))
    content_length = len(content_text)

    # Score simples: tamanho do conteúdo + peso de headings
    score = content_length + (h_count * 80) + (len(meta_desc) * 2)

    snippet = content_text[:240] + ("..." if len(content_text) > 240 else "")

    return {
        "title": title,
        "meta_description": meta_desc,
        "h1": h1,
        "content_snippet": snippet,
        "content_length": content_length,
        "score": score,
    }


def crawl_site(base_url: str, max_pages: int, delay: float) -> list:
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    })

    base_domain = urlparse(base_url).netloc.replace("www.", "").lower()
    rp = build_robot_parser(base_url)

    visited = set()
    queue = deque([base_url])
    results = []

    while queue and len(visited) < max_pages:
        url = queue.popleft()
        url = clean_url(url)
        if not url or url in visited:
            continue

        if rp and not rp.can_fetch("*", url):
            visited.add(url)
            continue

        try:
            resp = session.get(url, timeout=15)
            if resp.status_code != 200:
                visited.add(url)
                continue

            content_type = resp.headers.get("Content-Type", "")
            if "text/html" not in content_type:
                visited.add(url)
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            data = extract_content(soup)
            data["url"] = url
            results.append(data)

            # Coletar links internos
            for a in soup.find_all("a", href=True):
                href = clean_url(urljoin(url, a["href"]))
                if not href:
                    continue
                if not same_domain(href, base_domain):
                    continue
                if href not in visited:
                    queue.append(href)

            visited.add(url)
            time.sleep(delay)
        except requests.RequestException:
            visited.add(url)
            continue

    return results


def save_csv(rows: list, output_file: str, top_n: int):
    # Ordenar por score e manter os top_n
    rows_sorted = sorted(rows, key=lambda x: x["score"], reverse=True)
    rows_top = rows_sorted[:top_n] if top_n else rows_sorted

    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "url",
            "title",
            "meta_description",
            "h1",
            "content_snippet",
            "content_length",
            "score",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_top)


def main():
    parser = argparse.ArgumentParser(description="Scraper para conteúdo relevante do site Durex ES")
    parser.add_argument("--url", default="https://www.durex.es/", help="URL base do site")
    parser.add_argument("--max-pages", type=int, default=30, help="Número máximo de páginas a visitar")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay entre requisições (segundos)")
    parser.add_argument("--top", type=int, default=20, help="Número de páginas mais relevantes a salvar")
    parser.add_argument("--output", default="durex_relevant_content.csv", help="Arquivo CSV de saída")
    args = parser.parse_args()

    rows = crawl_site(args.url, args.max_pages, args.delay)
    if not rows:
        print("Nenhuma página foi processada.")
        return

    save_csv(rows, args.output, args.top)
    print(f"✅ CSV gerado com {min(args.top, len(rows))} páginas em '{args.output}'")


if __name__ == "__main__":
    main()
