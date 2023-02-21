import duckdb
from fastapi import HTTPException
import os
from urllib import request

from loguru import logger


def FetchTpchData():
    if not os.path.isfile("lineitemsf1.snappy.parquet"):
        logger.info("File not found, downloading!")
        url = (
            "https://github.com/duckdb/duckdb-data/releases/download"
            "/v1.0/lineitemsf1.snappy.parquet"
        )
        request.urlretrieve(url, "lineitemsf1.snappy.parquet")
        logger.success("File downloaded successfully!")


def ConnectDB():
    con = duckdb.connect()
    con.install_extension("substrait")
    con.load_extension("substrait")
    con.install_extension("tpch")
    con.load_extension("tpch")
    con.execute(
        query="CREATE TABLE IF NOT EXISTS lineitem"
        " AS SELECT * FROM 'lineitemsf1.snappy.parquet';"
    )
    logger.success("DuckDb initialized successfully")
    return con


def InitializeDB():
    FetchTpchData()
    return ConnectDB()


def CheckDuckDBConnection(con):
    status = {"db_health": "unavailable"}
    try:
        con.execute(query="SHOW TABLES;").fetchall()
        status["db_health"] = "up and running"
    except Exception as e:
        logger.info(
            "Healthcheck failed for DuckDB"
            "Initializing new connection object. Details: ",
            str(e),
        )
    finally:
        return status


def ExecuteDuckDb(data, con):
    try:
        if CheckDuckDBConnection(con)["db_health"] != "up and running":
            FetchTpchData()
            con = ConnectDB()
        for i in data:
            con.execute(query=i)
        return {"message": "DuckDB Operation successful"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Substrait DuckDB Internal Error while executing"
            "SQL Query: " + str(e),
        )


def ParseFromDuckDB(data, con):
    try:
        if CheckDuckDBConnection(con)["db_health"] != "up and running":
            FetchTpchData()
            con = ConnectDB()
        result = con.get_substrait_json(data["query"]).fetchone()[0]
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Substrait DuckDB Internal Error while parsing SQL Query: " + str(e),
        )
