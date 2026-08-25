# clean_data.py

import pandas as pd
import re

from config import (
    RAW_FILE,
    CLEAN_FILE
)


# ============================================================
# NORMALIZE COMPANY NAME
# ============================================================

def normalize_company(name):

    if pd.isna(name):

        return ""

    name = re.sub(
        r"\s+More Info\s*$",
        "",
        str(name),
        flags=re.IGNORECASE
    ).upper()

    # Remove punctuation

    name = re.sub(
        r"[^A-Z0-9 ]",
        " ",
        name
    )

    # Company suffixes

    suffixes = [
        "LLC",
        "L L C",
        "LTD",
        "LIMITED",
        "SPC",
        "FZE",
        "FZC",
        "CO",
        "COMPANY"
    ]

    for suffix in suffixes:

        name = re.sub(
            rf"\b{suffix}\b",
            " ",
            name
        )

    name = re.sub(
        r"\s+",
        " ",
        name
    )

    return name.strip()


# ============================================================
# PHONE CLEANING
# ============================================================

def clean_phone(phone):

    if pd.isna(phone):

        return ""

    phone = str(phone).strip()

    if phone.endswith(".0"):

        phone = phone[:-2]

    phone = re.sub(
        r"[^\d+]",
        "",
        phone
    )

    if phone and not phone.startswith("+") and len(phone) in [8, 9]:

        phone = "0" + phone

    return phone


def clean_city(city, location):

    if pd.notna(city) and str(city).strip():

        return str(city).strip()

    match = re.search(
        r"\bCity\s*:\s*(.*?)(?:\s+P\.?\s*O\.?\s+Box|\s+Phone\s*:|$)",
        str(location)
    )

    return match.group(1).strip() if match else ""


# ============================================================
# CATEGORY
# ============================================================

def classify_company(row):

    text = (
        str(row["company"]) +
        " " +
        str(row["location"])
    ).lower()

    if "mep" in text:

        return "MEP"

    if "electromechanical" in text:

        return "Electromechanical"

    if "hvac" in text:

        return "HVAC"

    if "plumbing" in text:

        return "Plumbing"

    if "electrical" in text:

        return "Electrical"

    if "mechanical" in text:

        return "Mechanical"

    if "technical services" in text:

        return "Technical Services"

    return "Other"


# ============================================================
# MAIN
# ============================================================

def main(input_file=RAW_FILE, output_file=CLEAN_FILE):

    print()
    print("=" * 70)
    print("DATA CLEANING")
    print("=" * 70)

    df = pd.read_csv(input_file)

    print(
        f"Raw rows: {len(df)}"
    )

    # --------------------------------------------------------
    # Normalize
    # --------------------------------------------------------

    df["company_normalized"] = (
        df["company"]
        .apply(normalize_company)
    )

    # --------------------------------------------------------
    # Phone
    # --------------------------------------------------------

    df["phone"] = (
        df["phone"]
        .apply(clean_phone)
    )

    df["city"] = df.apply(
        lambda row: clean_city(row["city"], row["location"]),
        axis=1
    )

    df["company"] = df["company"].apply(
        lambda value: re.sub(
            r"\s+More Info\s*$",
            "",
            str(value),
            flags=re.IGNORECASE
        ).strip()
    )

    # --------------------------------------------------------
    # Category
    # --------------------------------------------------------

    df["category"] = (
        df.apply(
            classify_company,
            axis=1
        )
    )

    # --------------------------------------------------------
    # Data quality
    # --------------------------------------------------------

    df["has_phone"] = (
        df["phone"]
        .str.len()
        .gt(0)
        .astype(int)
    )

    df["has_location"] = (
        df["location"]
        .fillna("")
        .str.len()
        .gt(10)
        .astype(int)
    )

    df["has_profile"] = (
        df["profile_url"]
        .fillna("")
        .str.len()
        .gt(10)
        .astype(int)
    )

    # --------------------------------------------------------
    # Remove empty company names
    # --------------------------------------------------------

    df = df[
        df["company_normalized"]
        .str.len()
        .gt(2)
    ]

    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    df = df.drop_duplicates(
        subset=[
            "company_normalized"
        ]
    )

    # --------------------------------------------------------
    # Remove irrelevant
    # --------------------------------------------------------

    valid = [
        "MEP",
        "Electromechanical",
        "HVAC",
        "Plumbing",
        "Electrical",
        "Mechanical",
        "Technical Services"
    ]

    df = df[
        df["category"]
        .isin(valid)
    ]

    # --------------------------------------------------------
    # Reset ID
    # --------------------------------------------------------

    df = df.reset_index(
        drop=True
    )

    df.insert(
        0,
        "record_id",
        range(
            1,
            len(df) + 1
        )
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    df.to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig"
    )

    print()
    print(
        f"Clean rows: {len(df)}"
    )

    print()
    print(
        "Categories:"
    )

    print(
        df["category"]
        .value_counts()
    )

    print()
    print(
        f"Saved: {output_file}"
    )


if __name__ == "__main__":

    main()