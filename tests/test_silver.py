from datetime import UTC, datetime

from orders.silver import deduplicate, standardize

BRONZE_DDL = """
    order_number STRING,
    customer_id STRING,
    customer_name STRING,
    order_datetime STRING,
    number_of_line_items STRING,
    ordered_products ARRAY<STRUCT<
        curr: STRING, id: STRING, name: STRING,
        price: STRING, qty: STRING, unit: STRING>>,
    _source_file STRING,
    _ingested_at TIMESTAMP
"""
PRODUCT = ("USD", "p1", "Camera", "448", "2", "pcs")
INGESTED = datetime(2026, 11, 1, tzinfo=UTC)


def bronze_row(order_number="1", ingested_at=INGESTED, source="a.json"):
    return (
        order_number,
        "19476252",
        "  Acme Corp ",
        "1564627663",
        "1",
        [PRODUCT],
        source,
        ingested_at,
    )


def test_standardize_casts_types_and_renames(spark):
    df = spark.createDataFrame([bronze_row()], BRONZE_DDL)

    row = standardize(df).collect()[0]

    assert row.order_id == 1
    assert row.customer_id == 19476252
    assert row.customer_name == "Acme Corp"
    assert row.line_item_count == 1
    assert row.ordered_at.astimezone(UTC).year == 2019
    assert row.products[0].asDict() == {
        "product_id": "p1",
        "product_name": "Camera",
        "price": 448.0,
        "quantity": 2,
        "unit": "pcs",
        "currency": "USD",
    }


def test_deduplicate_keeps_latest_ingested_row(spark):
    newer = datetime(2026, 11, 2, tzinfo=UTC)
    rows = [
        bronze_row("1", INGESTED, "old.json"),
        bronze_row("1", newer, "new.json"),
        bronze_row("2", INGESTED, "old.json"),
    ]
    df = standardize(spark.createDataFrame(rows, BRONZE_DDL))

    result = {r.order_id: r._source_file for r in deduplicate(df).collect()}

    assert result == {1: "new.json", 2: "old.json"}
