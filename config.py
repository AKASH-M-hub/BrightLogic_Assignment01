# config.py

# ============================================================
# PUBLIC UAE DIRECTORIES
# ============================================================

SOURCES = {

    "yellowpages_electromechanical":
        "https://www.yellowpages-uae.com/uae/electromechanical-contractors",

    "yellowpages_mep":
        "https://www.yellowpages-uae.com/uae/mep-contracting",

    "uae_yellowpages_mep":
        "https://www.uae-yellowpages.ae/listing-category/mep-contractors/",

    "uae_yellowpages_electromechanical":
        "https://www.uae-yellowpages.ae/listing-category/electromechanical-contractors/",

}


# ============================================================
# HOW MANY PAGES TO COLLECT
# ============================================================

# Yellow Pages shows 20 records per page.
#
# 5 pages × 20 = approximately 100 records
#
# We collect more than 100 because duplicates will exist.

PAGES_PER_SOURCE = 5


# ============================================================
# TARGET
# ============================================================

TARGET_COMPANIES = 100


# ============================================================
# DELAY BETWEEN REQUESTS
# ============================================================

REQUEST_DELAY = 2


# ============================================================
# OUTPUT FILES
# ============================================================

RAW_FILE = "raw_mep_data.csv"

CLEAN_FILE = "clean_mep_data.csv"

ML_FILE = "mep_top_100.csv"

EXCEL_FILE = "UAE_MEP_TOP_100.xlsx"