import pandas as pd
from urllib.parse import urljoin

from config import (
    ML_FILE,
    EXCEL_FILE
)


def main(
    input_file=ML_FILE,
    excel_file=EXCEL_FILE,
    csv_file="UAE_MEP_TOP_100.csv"
):

    print()
    print("=" * 70)
    print("EXPORTING FINAL DATA")
    print("=" * 70)

    df = pd.read_csv(input_file, dtype={"phone": "string"})

    df["company_url"] = df.apply(
        lambda row: urljoin(
            str(row.get("source", "")),
            str(row.get("profile_url", ""))
        ),
        axis=1
    )

    final_columns = [
        "rank",
        "company",
        "city",
        "location",
        "phone",
        "category",
        "lead_score",
        "priority",
        "ml_cluster",
        "company_url"
    ]

    final_columns = [
        col
        for col in final_columns
        if col in df.columns
    ]

    final_df = df[
        final_columns
    ]

    with pd.ExcelWriter(
        excel_file,
        engine="openpyxl"
    ) as writer:

        final_df.to_excel(
            writer,
            index=False,
            sheet_name="TOP_100_MEP"
        )

        summary = pd.DataFrame({
            "Metric": [
                "Total companies",
                "High priority",
                "Medium priority",
                "Low priority",
                "Companies with phone",
                "Cities covered"
            ],
            "Value": [
                len(final_df),
                (final_df["priority"] == "HIGH").sum(),
                (final_df["priority"] == "MEDIUM").sum(),
                (final_df["priority"] == "LOW").sum(),
                final_df["phone"].fillna("").astype(str).str.len().gt(0).sum(),
                final_df["city"].nunique()
            ]
        })

        summary.to_excel(
            writer,
            index=False,
            sheet_name="SUMMARY"
        )

    final_df.to_csv(
        csv_file,
        index=False,
        encoding="utf-8-sig"
    )

    print()
    print(
        f"Excel created: {excel_file}"
    )

    print(
        f"CSV created: {csv_file}"
    )


if __name__ == "__main__":

    main()