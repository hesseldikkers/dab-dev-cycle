from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from orders.args import parse_args


def ingest(spark: SparkSession, catalog: str, schema: str) -> None:
    base = f"/Volumes/{catalog}/{schema}"
    (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option(
            "cloudFiles.schemaLocation",
            f"{base}/checkpoints/bronze/schema",
        )
        .load(f"{base}/landing/sales_orders/")
        .withColumn("_source_file", F.col("_metadata.file_path"))
        .withColumn("_ingested_at", F.current_timestamp())
        .writeStream.option(
            "checkpointLocation", f"{base}/checkpoints/bronze/orders"
        )
        .trigger(availableNow=True)
        .toTable(f"{catalog}.{schema}.orders_bronze")
        .awaitTermination()
    )


def main() -> None:
    args = parse_args()
    ingest(SparkSession.builder.getOrCreate(), args.catalog, args.schema)
