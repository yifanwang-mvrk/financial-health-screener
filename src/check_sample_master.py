from pathlib import Path
import sys
import pandas as pd


DATA_PATH = Path("data/raw/sample_companies_master.csv")

EXPECTED_COLUMNS = [
    "ticker",
    "company_name",
    "exchange",
    "country",
    "listing_status",
    "primary_business_model",
    "secondary_business_model",
    "platform_type",
    "has_marketplace",
    "has_first_party_retail",
    "has_subscription",
    "has_payment_fintech",
    "has_ads_business",
    "peer_group",
    "include_in_core_sample",
    "include_reason",
    "exclude_reason",
    "notes",
]

ALLOWED_BINARY = {"0", "1"}

ALLOWED_LISTING_STATUS = {
    "active",
    "delisted",
    "delisted_acquired",
    "bankrupt",
    "acquired",
}

ALLOWED_PEER_GROUPS = {
    "hybrid_retail_marketplace",
    "marketplace",
    "first_party_retail",
    "food_delivery_local_commerce",
    "travel_booking_platform",
    "merchant_enablement",
    "service_commerce_platform",
}

ALLOWED_PRIMARY_MODELS = {
    "hybrid_retail_marketplace",
    "marketplace",
    "first_party_retail",
    "food_delivery_local_commerce",
    "travel_booking_platform",
    "merchant_enablement",
    "service_commerce_platform",
}


def fail(message: str) -> None:
    print(f"❌ {message}")
    sys.exit(1)


def main() -> None:
    if not DATA_PATH.exists():
        fail(f"File not found: {DATA_PATH}")

    # keep_default_na=False is important because the CSV uses 'NA' as a text label.
    df = pd.read_csv(DATA_PATH, dtype=str, keep_default_na=False)

    print("=== Sample Master Quality Check ===")
    print(f"File: {DATA_PATH}")
    print(f"Shape: {df.shape}")

    if list(df.columns) != EXPECTED_COLUMNS:
        print("\nExpected columns:")
        print(EXPECTED_COLUMNS)
        print("\nActual columns:")
        print(list(df.columns))
        fail("Column structure does not match expected schema.")

    if df.empty:
        fail("CSV has no company rows.")

    # Strip whitespace from all string cells before validation.
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    duplicate_tickers = df[df["ticker"].duplicated(keep=False)]["ticker"].tolist()
    if duplicate_tickers:
        fail(f"Duplicate tickers found: {duplicate_tickers}")

    required_non_empty = [
        "ticker",
        "company_name",
        "exchange",
        "country",
        "listing_status",
        "primary_business_model",
        "platform_type",
        "peer_group",
        "include_in_core_sample",
    ]

    for col in required_non_empty:
        empty_count = (df[col] == "").sum()
        if empty_count > 0:
            fail(f"Column '{col}' has {empty_count} empty values.")

    binary_cols = [
        "has_marketplace",
        "has_first_party_retail",
        "has_subscription",
        "has_payment_fintech",
        "has_ads_business",
        "include_in_core_sample",
    ]

    for col in binary_cols:
        invalid_values = sorted(set(df[col]) - ALLOWED_BINARY)
        if invalid_values:
            fail(f"Column '{col}' has invalid values: {invalid_values}. Allowed values are 0 or 1.")

    invalid_listing_status = sorted(set(df["listing_status"]) - ALLOWED_LISTING_STATUS)
    if invalid_listing_status:
        fail(f"Invalid listing_status values: {invalid_listing_status}")

    invalid_peer_groups = sorted(set(df["peer_group"]) - ALLOWED_PEER_GROUPS)
    if invalid_peer_groups:
        fail(f"Invalid peer_group values: {invalid_peer_groups}")

    invalid_primary_models = sorted(set(df["primary_business_model"]) - ALLOWED_PRIMARY_MODELS)
    if invalid_primary_models:
        fail(f"Invalid primary_business_model values: {invalid_primary_models}")

    print("\n✅ Column schema check passed.")
    print("✅ Duplicate ticker check passed.")
    print("✅ Required field check passed.")
    print("✅ Binary field check passed.")
    print("✅ Listing status check passed.")
    print("✅ Peer group check passed.")
    print("✅ Primary business model check passed.")

    print("\nCore sample flag count:")
    print(df["include_in_core_sample"].value_counts().sort_index())

    print("\nListing status count:")
    print(df["listing_status"].value_counts())

    print("\nPeer group count:")
    print(df["peer_group"].value_counts())

    print("\n✅ All sample master checks passed.")


if __name__ == "__main__":
    main()
