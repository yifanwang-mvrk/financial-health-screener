from pathlib import Path

import duckdb

db_path = Path("db/financial_health_screener.duckdb")
sql_path = Path("sql/mvp_analysis_rebuild.sql")

sql = sql_path.read_text()

with duckdb.connect(str(db_path), read_only=True) as connection:
    result = connection.execute(sql).fetchdf()

print(result.to_string(index=False))
print(f"\nRows returned: {len(result)}")