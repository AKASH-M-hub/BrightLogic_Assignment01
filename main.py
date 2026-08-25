# main.py

import collect_data
import clean_data
import ml_analysis
import export_results


def main():

    print()
    print("=" * 80)
    print("UAE MEP TOP 100 - FREE DATA ENGINEERING + ML")
    print("=" * 80)

    # --------------------------------------------------------
    # STEP 1
    # --------------------------------------------------------

    print()
    print("STEP 1/4")
    print("Collecting public UAE MEP data...")

    collect_data.main()

    # --------------------------------------------------------
    # STEP 2
    # --------------------------------------------------------

    print()
    print("STEP 2/4")
    print("Cleaning and deduplicating...")

    clean_data.main()

    # --------------------------------------------------------
    # STEP 3
    # --------------------------------------------------------

    print()
    print("STEP 3/4")
    print("Running ML and ranking...")

    ml_analysis.main()

    # --------------------------------------------------------
    # STEP 4
    # --------------------------------------------------------

    print()
    print("STEP 4/4")
    print("Creating Excel and CSV...")

    export_results.main()

    print()
    print("=" * 80)
    print("DONE")
    print("=" * 80)

    print()
    print(
        "Final files:"
    )

    print(
        "UAE_MEP_TOP_100.xlsx"
    )

    print(
        "UAE_MEP_TOP_100.csv"
    )


if __name__ == "__main__":

    main()