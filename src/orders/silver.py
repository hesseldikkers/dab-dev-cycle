from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from orders.location import Location, Table

PRODUCTS = (
    "array<struct<curr:string, id:string, name:string,"
    " price:double, qty:int, unit:string>>"
)


def standardize(df: DataFrame) -> DataFrame:
    return df.select(
        F.col("order_number").cast("bigint").alias("order_id"),
        F.col("customer_id").cast("bigint"),
        F.trim("customer_name").alias("customer_name"),
        F.timestamp_seconds(F.col("order_datetime").cast("bigint")).alias(
            "ordered_at"
        ),
        F.from_json("ordered_products", PRODUCTS).alias("products"),
    ).dropDuplicates(["order_id"])


def upsert(df: DataFrame, table: str) -> None:
    spark = df.sparkSession
    if not spark.catalog.tableExists(table):
        df.write.saveAsTable(table)
        return

    df.createOrReplaceTempView("updates")
    spark.sql(
        f"""
        MERGE INTO {table} t
        USING updates s ON t.order_id = s.order_id
        WHEN MATCHED THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
        """
    )


def main() -> None:
    location = Location.from_args()
    spark = SparkSession.builder.getOrCreate()
    bronze = spark.read.table(location.table(Table.BRONZE))
    upsert(standardize(bronze), location.table(Table.SILVER))
