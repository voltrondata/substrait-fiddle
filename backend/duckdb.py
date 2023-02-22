import duckdb
from fastapi import HTTPException

from loguru import logger

schema_lineitem = """CREATE TABLE IF NOT EXISTS lineitem(
            l_orderkey INTEGER NOT NULL, 
            l_partkey INTEGER NOT NULL, 
            l_suppkey INTEGER NOT NULL, 
            l_linenumber INTEGER NOT NULL, 
            l_quantity INTEGER NOT NULL, 
            l_extendedprice DECIMAL(15,2) NOT NULL, 
            l_discount DECIMAL(15,2) NOT NULL, 
            l_tax DECIMAL(15,2) NOT NULL, 
            l_returnflag VARCHAR NOT NULL, 
            l_linestatus VARCHAR NOT NULL, 
            l_shipdate DATE NOT NULL, 
            l_commitdate DATE NOT NULL, 
            l_receiptdate DATE NOT NULL, 
            l_shipinstruct VARCHAR NOT NULL, 
            l_shipmode VARCHAR NOT NULL, 
            l_comment VARCHAR NOT NULL);"""


def ConnectDuckDB():
    con = duckdb.connect()
    con.install_extension("substrait")
    con.load_extension("substrait")
    con.install_extension("tpch")
    con.load_extension("tpch")
    con.execute(query=schema_lineitem)
    logger.success("DuckDb initialized successfully")
    return con


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
            con = ConnectDuckDB()
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
            con = ConnectDuckDB()
        result = con.get_substrait_json(data["query"]).fetchone()[0]
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Substrait DuckDB Internal Error while parsing SQL Query: " + str(e),
        )
