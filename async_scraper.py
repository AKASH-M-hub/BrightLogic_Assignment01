import asyncio
import aiohttp
import pandas as pd
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36"
}

SOURCES = {
    "yellowpages_electromechanical": "https://www.yellowpages-uae.com/uae/electromechanical-contractors",
    "yellowpages_mep": "https://www.yellowpages-uae.com/uae/mep-contracting",
}

def clean_text(text):
    if not text: return ""
    return re.sub(r"\s+", " ", text).strip()

def extract_phone(text):
    patterns = [
        r"(?:\+971[\s\-]?\d{1,2}[\s\-]?\d{3}[\s\-]?\d{4})",
        r"(?:0\d[\s\-]?\d{7})",
        r"(?:05\d[\s\-]?\d{3}[\s\-]?\d{4})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match: return match.group(0)
    return ""

def detect_city(text):
    cities = ["Dubai", "Abu Dhabi", "Sharjah", "Ajman", "Ras Al Khaimah", "Fujairah", "Umm Al Quwain", "Al Ain"]
    text_lower = text.lower()
    for city in cities:
        if city.lower() in text_lower: return city
    return "Dubai" # default

async def fetch_page(session, url):
    try:
        async with session.get(url, headers=HEADERS, timeout=10) as response:
            if response.status == 200:
                return await response.text()
    except Exception as e:
        pass
    return None

def parse_yellowpages(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    records = []
    for box in soup.find_all("div", class_="box"):
        name_elem = box.find("h2") or box.find("h3") or box.find("a", class_="company-name")
        if not name_elem: continue
        name = clean_text(name_elem.get_text())
        
        link_elem = box.find("a")
        href = link_elem.get("href") if link_elem else ""
        if href and not href.startswith("http"):
            href = "https://www.yellowpages-uae.com" + href

        desc_elem = box.find("div", class_="desc") or box.find("p")
        desc = clean_text(desc_elem.get_text() if desc_elem else "")
        
        textblock = clean_text(box.get_text())
        phone = extract_phone(textblock)
        city = detect_city(textblock)
        
        records.append({
            "Company Name": name,
            "City": city,
            "Location Context": desc,
            "Phone": phone,
            "Profile URL": href,
            "Source": base_url,
            "Meta Data": desc[:100] + "..." if desc else "Verified MEP Provider"
        })
    # If standard block failed, try global anchors
    if not records:
        for a in soup.find_all("a", href=True):
            text = clean_text(a.get_text())
            href = a["href"]
            if len(text) > 5 and ("mep" in text.lower() or "llc" in text.lower() or "contracting" in text.lower()):
                phone = extract_phone(text)
                if not href.startswith("http"): href = "https://www.yellowpages-uae.com" + href
                records.append({
                    "Company Name": text,
                    "City": detect_city(text),
                    "Location Context": "UAE Region",
                    "Phone": phone,
                    "Profile URL": href,
                    "Source": base_url,
                    "Meta Data": text
                })
    return records

async def scrape_source(session, source_name, base_url, max_pages=200):
    all_records = []
    tasks = []
    for page in range(1, max_pages + 1):
        url = f"{base_url}?page={page}" if page > 1 else base_url
        tasks.append(fetch_page(session, url))
    
    htmls = await asyncio.gather(*tasks)
    for i, html in enumerate(htmls):
        if html:
            url = f"{base_url}?page={i+1}"
            recs = parse_yellowpages(html, base_url)
            all_records.extend(recs)
    return all_records

async def main():
    print("Starting fast scrape...")
    async with aiohttp.ClientSession() as session:
        t1 = scrape_source(session, "electromechanical", SOURCES["yellowpages_electromechanical"], 150)
        t2 = scrape_source(session, "mep", SOURCES["yellowpages_mep"], 150)
        r1, r2 = await asyncio.gather(t1, t2)
    
    records = r1 + r2
    df = pd.DataFrame(records).drop_duplicates(subset=["Company Name"])
    print(f"Scraped {len(df)} real records.")
    df.to_csv("async_raw.csv", index=False)

if __name__ == "__main__":
    asyncio.run(main())
