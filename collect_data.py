# collect_data.py

import requests
import pandas as pd
import time
import re

from bs4 import BeautifulSoup

from config import (
    SOURCES,
    PAGES_PER_SOURCE,
    REQUEST_DELAY,
    RAW_FILE
)


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/151.0 Safari/537.36"
    )
}


# ============================================================
# DOWNLOAD PAGE
# ============================================================

def get_page(url):

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=30
        )

        if response.status_code == 200:

            return response.text

        print(
            f"Request failed: "
            f"{response.status_code}"
        )

    except Exception as e:

        print(
            f"Request error: {e}"
        )

    return None


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text):

    if not text:
        return ""

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# EXTRACT PHONE NUMBERS
# ============================================================

def extract_phone(text):

    patterns = [

        r"(?:\+971[\s\-]?\d{1,2}[\s\-]?\d{3}[\s\-]?\d{4})",

        r"(?:0\d[\s\-]?\d{7})",

        r"(?:05\d[\s\-]?\d{3}[\s\-]?\d{4})",

        r"(?:04[\s\-]?\d{7})",

        r"(?:02[\s\-]?\d{7})",

        r"(?:06[\s\-]?\d{7})",

        r"(?:07[\s\-]?\d{7})",

        r"(?:03[\s\-]?\d{7})"

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text
        )

        if match:

            return match.group(0)

    return ""


# ============================================================
# CITY DETECTION
# ============================================================

def detect_city(text):

    cities = [
        "Dubai",
        "Abu Dhabi",
        "Sharjah",
        "Ajman",
        "Ras Al Khaimah",
        "Fujairah",
        "Umm Al Quwain",
        "Al Ain"
    ]

    text_lower = text.lower()

    for city in cities:

        if city.lower() in text_lower:

            return city

    return ""


# ============================================================
# YELLOW PAGES PARSER
# ============================================================

def parse_yellowpages(html, source_url):

    soup = BeautifulSoup(
        html,
        "lxml"
    )

    records = []

    # --------------------------------------------------------
    # Find company profile links
    # --------------------------------------------------------

    links = soup.find_all(
        "a",
        href=True
    )

    seen = set()

    for link in links:

        name = clean_text(
            link.get_text(
                " ",
                strip=True
            )
        )

        href = link.get(
            "href"
        )

        if not name:
            continue

        if not href:
            continue

        # ----------------------------------------------------
        # Avoid navigation links
        # ----------------------------------------------------

        if len(name) < 3:
            continue

        if name.lower() in [
            "read more",
            "website",
            "directions",
            "brochure",
            "branches",
            "send enquiry"
        ]:
            continue

        # ----------------------------------------------------
        # Look around the company link
        # ----------------------------------------------------

        parent = link.parent

        if parent:

            block = parent.parent

        else:

            block = link

        text = clean_text(
            block.get_text(
                " ",
                strip=True
            )
        )

        # ----------------------------------------------------
        # Company relevance
        # ----------------------------------------------------

        keywords = [
            "electromechanical",
            "mep",
            "mechanical",
            "electrical",
            "hvac",
            "plumbing",
            "technical services"
        ]

        relevant = any(
            keyword in text.lower()
            for keyword in keywords
        )

        if not relevant:
            continue

        phone = extract_phone(
            text
        )

        city = detect_city(
            text
        )

        key = (
            name.lower(),
            city.lower()
        )

        if key in seen:
            continue

        seen.add(key)

        records.append({

            "company": name,

            "location": text,

            "city": city,

            "phone": phone,

            "source": source_url,

            "profile_url": href

        })

    return records


# ============================================================
# GENERIC PARSER
# ============================================================

def parse_generic(html, source_url):

    soup = BeautifulSoup(
        html,
        "lxml"
    )

    records = []

    headings = soup.find_all(
        ["h2", "h3"]
    )

    for heading in headings:

        company = clean_text(
            heading.get_text(
                " ",
                strip=True
            )
        )

        if not company:
            continue

        parent = heading.parent

        if not parent:
            continue

        text = clean_text(
            parent.get_text(
                " ",
                strip=True
            )
        )

        phone = extract_phone(
            text
        )

        city = detect_city(
            text
        )

        records.append({

            "company": company,

            "location": text,

            "city": city,

            "phone": phone,

            "source": source_url,

            "profile_url": ""

        })

    return records


# ============================================================
# MAIN
# ============================================================

def main():

    all_records = []

    print()
    print("=" * 70)
    print("UAE MEP FREE DATA COLLECTION")
    print("=" * 70)

    for source_name, base_url in SOURCES.items():

        print()
        print(
            f"SOURCE: {source_name}"
        )

        for page in range(
            1,
            PAGES_PER_SOURCE + 1
        ):

            # ------------------------------------------------
            # Yellow Pages pagination
            # ------------------------------------------------

            if "yellowpages-uae.com" in base_url:

                if page == 1:

                    url = base_url

                else:

                    url = (
                        f"{base_url}"
                        f"?page={page}"
                    )

            else:

                if page == 1:

                    url = base_url

                else:

                    url = (
                        f"{base_url}"
                        f"?page={page}"
                    )

            print(
                f"Page {page}: {url}"
            )

            html = get_page(
                url
            )

            if not html:

                continue

            # ------------------------------------------------
            # Parse
            # ------------------------------------------------

            if "yellowpages-uae.com" in base_url:

                records = parse_yellowpages(
                    html,
                    url
                )

            else:

                records = parse_generic(
                    html,
                    url
                )

            print(
                f"Records found: "
                f"{len(records)}"
            )

            all_records.extend(
                records
            )

            time.sleep(
                REQUEST_DELAY
            )

    # ========================================================
    # SAVE RAW DATA
    # ========================================================

    df = pd.DataFrame(
        all_records
    )

    if df.empty:

        print()
        print(
            "NO DATA FOUND."
        )

        print(
            "A directory may have changed "
            "its HTML structure."
        )

        return

    df.to_csv(
        RAW_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print()
    print("=" * 70)
    print("COLLECTION FINISHED")
    print("=" * 70)

    print(
        f"Raw records: {len(df)}"
    )

    print(
        f"Saved: {RAW_FILE}"
    )


if __name__ == "__main__":

    main()