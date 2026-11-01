CREATE OR REPLACE TABLE IDENTIFIER(:catalog || '.' || :schema || '.orders_daily') AS
WITH lines AS (
  SELECT
    order_id,
    customer_id,
    CAST(ordered_at AS DATE) AS order_date,
    product.price * product.qty AS line_total
  FROM IDENTIFIER(:catalog || '.' || :schema || '.orders_silver')
  LATERAL VIEW EXPLODE(products) AS product
)
SELECT
  order_date,
  COUNT(DISTINCT order_id) AS order_count,
  COUNT(DISTINCT customer_id) AS customer_count,
  SUM(line_total) AS revenue
FROM lines
GROUP BY order_date
