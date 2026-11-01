from pyspark.sql import DataFrame, SparkSession, Window
from pyspark.sql import functions as F

from orders.args import parse_args


def standardize(df: DataFrame) -> DataFrame:
    return df.select(
        F.col("order_number").cast("long").alias("order_id"),
        F.col("customer_id").cast("long").alias("customer_id"),
        F.trim("customer_name").alias("customer_name"),
        F.col("order_datetime")
        .cast("long")
        .cast("timestamp")
        .alias("ordered_at"),
        F.col("number_of_line_items").cast("int").alias("line_item_count"),
        F.transform(
            "ordered_products",
            lambda p: F.struct(
                p["id"].alias("product_id"),
                p["name"].alias("product_name"),
                p["price"].cast("double").alias("price"),
                p["qty"].cast("int").alias("quantity"),
                p["unit"].alias("unit"),
                p["curr"].alias("currency"),
            ),
        ).alias("products"),
        "_source_file",
        "_ingested_at",
    )


def deduplicate(df: DataFrame) -> DataFrame:
    latest_first = Window.partitionBy("order_id").orderBy(
        F.col("_ingested_at").desc(), F.col("_source_file").desc()
    )
    return (
        df.withColumn("_rank", F.row_number().over(latest_first))
        .filter(F.col("_rank") == 1)
        .drop("_rank")
    )


def merge(spark: SparkSession, df: DataFrame, target: str) -> None:
    df.limit(0).writeTo(target).createIfNotExists()
    df.createOrReplaceTempView("order_updates")
    spark.sql(
        f"""
        MERGE INTO {target} AS t
        USING order_updates AS s
        ON t.order_id = s.order_id
        WHEN MATCHED THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
        """
    )


def main() -> None:
    args = parse_args()
    spark = SparkSession.builder.getOrCreate()
    prefix = f"{args.catalog}.{args.schema}"
    bronze = spark.read.table(f"{prefix}.orders_bronze")
    merge(spark, deduplicate(standardize(bronze)), f"{prefix}.orders_silver")
