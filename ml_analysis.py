import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

from config import (
    CLEAN_FILE,
    ML_FILE,
    TARGET_COMPANIES
)


def main():

    print()
    print("=" * 70)
    print("ML ANALYSIS AND RANKING")
    print("=" * 70)

    df = pd.read_csv(
        CLEAN_FILE
    )

    df["lead_score"] = (
        40 * df["category"].isin([
            "MEP",
            "Electromechanical",
            "Mechanical",
            "Electrical",
            "HVAC",
            "Plumbing"
        ]).astype(int)
        + 25 * df["has_phone"]
        + 15 * df["has_location"]
        + 10 * df["has_profile"]
        + 10 * df["company"].fillna("").str.len().clip(upper=30).div(30)
    ).round(1)

    text = (
        df["company"].fillna("") + " "
        + df["category"].fillna("") + " "
        + df["location"].fillna("")
    )

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1
    )
    features = vectorizer.fit_transform(text)
    cluster_count = min(4, max(2, len(df) // 10))
    df["ml_cluster"] = KMeans(
        n_clusters=cluster_count,
        random_state=42,
        n_init=10
    ).fit_predict(features)

    df["priority"] = pd.cut(
        df["lead_score"],
        bins=[-1, 59, 79, 100],
        labels=["LOW", "MEDIUM", "HIGH"]
    ).astype(str)

    df = df.sort_values(
        "lead_score",
        ascending=False
    ).head(TARGET_COMPANIES).copy()

    df.insert(
        0,
        "rank",
        range(1, len(df) + 1)
    )

    df.to_csv(
        ML_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print(
        f"Ranked companies: {len(df)}"
    )
    print(
        f"Saved: {ML_FILE}"
    )


if __name__ == "__main__":

    main()
