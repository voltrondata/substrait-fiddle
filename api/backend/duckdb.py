import duckdb
from fastapi import HTTPException

from loguru import logger


class DuckDBConnection:
    def __init__(self):
        self.conn_pool = []

        query_lineitem = '''CREATE TABLE IF NOT EXISTS lineitem(
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
                        l_comment VARCHAR NOT NULL);'''
        conn = duckdb.connect("duck.db")
        conn.execute(query=query_lineitem)
        
        for i in range(5):
            conn = duckdb.connect("duck.db")
            conn.install_extension("substrait")
            conn.load_extension("substrait")
            self.conn_pool.append(conn)


    def check_pool(self):
        if len(self.conn_pool) == 0:
            print("creating new conn objects")
            for i in range(5):
                conn = duckdb.connect()
                conn.install_extension("substrait")
                conn.load_extension("substrait")
                self.conn_pool.append(conn)

    def initialize(self):
        self.check_pool()
        con = self.conn_pool.pop(0)
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


def ExecuteDuckDb(query, con):
    try:
        con.execute(query = query)
        return {"message": "DuckDB Operation successful"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Substrait DuckDB Internal Error while executing"
            "SQL Query: " + str(e),
        )


def ParseFromDuckDB(data, con):
    try:
        result = con.get_substrait_json(data["query"]).fetchone()[0]
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Substrait DuckDB Internal Error while parsing SQL Query: " + str(e),
        )
