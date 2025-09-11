import os
from pathlib import Path
from app.config.env import load_env
import MySQLdb

# Runs statements saved in sql file
def run_sql_file(cur, path: Path):
    sql_text = path.read_text(encoding="utf-8")

    for statement in (s.strip() for s in sql_text.split(";")):
        if statement:
            try:
                cur.execute(statement)
            except MySQLdb.OperationalError as e:
                code = getattr(e, "args", [None])[0]
                known = {1007, 1050, 1061}
                if code in known:
                    print(f"[idempotent-ok] {code} on: {statement[:120]!r}")
                else:
                    raise

# setup db main function
def main():
    # load variables and pull connection info
    load_env()
    host = os.getenv("SA_DB_HOST", "localhost")
    port = int(os.getenv("SA_DB_PORT", "3306"))
    user = os.getenv("SA_DB_USER", "root")
    passwd = os.getenv("SA_DB_PASS", "")
    dbname = os.getenv("SA_DB_NAME", "the_studentr")

    # connect to db
    conn = MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, charset="utf8mb4", use_unicode=True)
    cur = conn.cursor()
    schema = Path("db/schema.sql")
    seed = Path("db/seed.sql")

    # apply schema.sql
    if schema.exists():
        try:
            run_sql_file(cur, schema)
            conn.commit()
        except:
            conn.rollback()
            raise

    # apply seed.sql
    if seed.exists():
        try:
            run_sql_file(cur, seed)
            conn.commit()
        except:
            conn.rollback()
            raise

    # sanity check - print tables
    cur.execute("SHOW TABLES")
    tables = [r[0] for r in cur.fetchall()]
    print("Tables: ", ", ".join(tables))
    for t in ("users", "modules", "assignments", "marks"):
        if t in tables:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            print(f"{t}: {cur.fetchone()[0]}")

    cur.close()
    conn.close()
    print(dbname, " has been set up successfully.")

# run main
if __name__ == "__main__":
    main()