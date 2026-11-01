import json

import pytest

from orders.silver import standardize, upsert

BRONZE_SCHEMA = (
    "order_number string, customer_id string, customer_name string,"
    " order_datetime string, ordered_products string"
)
PRODUCTS = [
    {
        "curr": "USD",
        "id": "p1",
        "name": "Camera",
        "price": 448,
        "qty": 2,
        "unit": "pcs",
    }
]


def bronze_row(order_number="1", customer_name="  Acme "):
    return (
        order_number,
        "19476252",
        customer_name,
        "1564627663",
        json.dumps(PRODUCTS),
    )


@pytest.fixture
def silver_table(spark):
    spark.sql("DROP TABLE IF EXISTS orders_silver_test")
    yield "orders_silver_test"
    spark.sql("DROP TABLE IF EXISTS orders_silver_test")


def test_standardize_casts_types_and_parses_products(spark):
    df = spark.createDataFrame([bronze_row()], BRONZE_SCHEMA)

    row = standardize(df).collect()[0]

    assert row.order_id == 1
    assert row.customer_id == 19476252
    assert row.customer_name == "Acme"
    assert row.ordered_at.year == 2019
    assert row.products[0].qty == 2
    assert row.products[0].price == 448.0


def test_standardize_drops_duplicate_orders(spark):
    rows = [bronze_row("1"), bronze_row("1"), bronze_row("2")]
    df = spark.createDataFrame(rows, BRONZE_SCHEMA)

    assert standardize(df).count() == 2


def test_upsert_creates_missing_table(spark, silver_table):
    df = standardize(spark.createDataFrame([bronze_row()], BRONZE_SCHEMA))

    upsert(df, silver_table)

    assert spark.table(silver_table).count() == 1
