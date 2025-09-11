from __future__ import annotations
import os
import sys
from app.dal.base import db_conn, fetch_all, fetch_one, ping

def main():
    print("DAL connectivity smoke")

    if not ping():
        print("Unable to connect with current SA_DB_* settings.", file=sys.stderr)
        sys.exit(2)
    print("Config:", {k: os.getenv(k) for k in ["SA_DB_HOST","SA_DB_PORT","SA_DB_USER","SA_DB_NAME"]})
    print("Connected to MySQL.")

    with db_conn() as conn:
        db_name = fetch_one(conn, "SELECT DATABASE() AS db")["db"]
        print("Using database:", db_name or "(none)")

        rows = fetch_all(conn,
            "SELECT TABLE_NAME AS table_name FROM information_schema.tables "
            "WHERE table_schema=%s ORDER BY TABLE_NAME",
            (db_name,))
        tables = [r["table_name"] for r in rows]
        print("Tables:", ", ".join(tables) if tables else "(none)")

        expected = ("USERS","MODULES","ASSIGNMENTS","MARKS")
        missing = [t for t in expected if t not in tables]
        if missing:
            print("Missing schema tables:", ", ".join(missing), file=sys.stderr)
            sys.exit(3)

        for t in expected:
            c = fetch_one(conn, f"SELECT COUNT(*) AS c FROM {t}")["c"]
            print(f"    - {t}: {c}")

    print("DAL Smoke Passed")
    return 0

if __name__ == "__main__":
    sys.exit(main())