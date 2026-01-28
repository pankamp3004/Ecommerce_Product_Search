import pandas as pd
from psycopg2.extras import execute_values
from indexing.db import get_pg_connection


DATA_PATH = "data/Fashion Data mini.csv"

NUMERIC_COLS = ["selling_price", "mrp", "star_rating"]
TEXT_COLS = ["title", "brand", "category", "colour"]

FINAL_COLS = [
    "product_id",
    "image_url",
    "product_url",
    "title",
    "product_details",
    "brand",
    "category",
    "colour",
    "size",
    "competitor",
    "selling_price",
    "mrp",
    "star_rating"
]


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS ecommerce_products_mini (
    product_id TEXT PRIMARY KEY,

    -- UI
    image_url TEXT,
    product_url TEXT,

    -- Core Search Text
    title TEXT,
    product_details TEXT,

    -- Filters (Categorical)
    brand TEXT,
    category TEXT,
    colour TEXT,
    size TEXT,
    competitor TEXT,

    -- Filters (Numeric)
    selling_price FLOAT,
    mrp FLOAT,
    star_rating FLOAT
);
"""


INSERT_SQL = """
INSERT INTO ecommerce_products_mini (
    product_id,
    image_url,
    product_url,
    title,
    product_details,
    brand,
    category,
    colour,
    size,
    competitor,
    selling_price,
    mrp,
    star_rating
)
VALUES %s
ON CONFLICT (product_id) DO NOTHING;
"""


# ----------------------------
# Step 1: Load CSV
# ----------------------------
def load_csv(path: str) -> pd.DataFrame:
    print(f"📥 Loading CSV from: {path}")
    df = pd.read_csv(path)
    print(f"✓ Loaded {len(df)} rows")
    return df


# ----------------------------
# Step 2: Clean & Normalize
# ----------------------------
def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    print("🧹 Cleaning dataframe...")

    # Replace NaN/NaT with None (DB + JSON safe)
    df = df.where(df.notna(), None)

    # Fix numeric columns
    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Rename columns
    df.rename(columns={
        "product_detials": "product_details",
        "uuid": "product_id",
        "url": "product_url",
        "images": "image_url"
    }, inplace=True)

    # Strip basic text columns
    for col in TEXT_COLS:
        df[col] = df[col].astype(str).str.strip()

    # Drop unwanted columns (if present)
    drop_cols = ["date_stored", "meta_data", "set_product_price"]
    existing = [c for c in drop_cols if c in df.columns]
    if existing:
        df.drop(columns=existing, inplace=True)

    # Select final columns
    df = df[FINAL_COLS]

    print("✓ Dataframe cleaned & normalized")
    return df


# ----------------------------
# Step 3: Create Table
# ----------------------------
def create_products_table(cursor):
    print("🗄️ Ensuring products table exists...")
    cursor.execute(CREATE_TABLE_SQL)
    print("✓ Table `ecommerce_products_mini` is ready")


# ----------------------------
# Step 4: Bulk Insert
# ----------------------------
def bulk_insert_products(cursor, df: pd.DataFrame):
    print("📤 Inserting records into PostgreSQL...")

    records = df.to_records(index=False).tolist()

    execute_values(
        cursor,
        INSERT_SQL,
        records,
        page_size=1000  # performance tuning
    )

    print(f"Inserted {len(records)} rows into ecommerce_products_mini")


# ----------------------------
# Step 5: Main Orchestrator
# ----------------------------
def main():
    print("Starting product load pipeline")

    # Load
    df = load_csv(DATA_PATH)

    # Clean
    df = clean_dataframe(df)

    # DB
    conn = get_pg_connection()
    cursor = conn.cursor()

    try:
        # Create table
        create_products_table(cursor)
        # Insert data
        bulk_insert_products(cursor, df)

        # Commit
        conn.commit()
        print("Pipeline completed successfully")

    except Exception as e:
        conn.rollback()
        print("Pipeline failed, rolling back")
        raise e

    finally:
        cursor.close()
        conn.close()
        print("DB connection closed")


# ----------------------------
# Entry Point
# ----------------------------
if __name__ == "__main__":
    main()
