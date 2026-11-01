from pathlib import Path

SQL_FILE = Path(__file__).parents[1] / "src/orders/sql/orders_daily.sql"


def test_mart_sql_uses_parameters_not_hardcoded_names():
    sql = SQL_FILE.read_text()

    assert ":catalog" in sql
    assert ":schema" in sql
    assert "workspace" not in sql
