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


class DuckDBConnection:
    def __init__(self):
        self.connection = None

    def connect(self):
        self.connection = duckdb.connect()
        self.connection.install_extension("substrait")
        self.connection.load_extension("substrait")
        self.connection.install_extension("tpch")
        self.connection.load_extension("tpch")
        self.connection.execute(query=schema_lineitem)
        logger.success("DuckDb initialized successfully")

    def check(self):
        status = {"db_health": "unavailable"}
        try:
            self.connection.execute(query="SHOW TABLES;").fetchall()
            status["db_health"] = "up and running"
        except Exception as e:
            logger.info(
                "Healthcheck failed for DuckDB"
                "Initializing new connection object. Details: ",
                str(e),
            )
        finally:
            return status

    def execute(self, data):
        try:
            if self.check()["db_health"] != "up and running":
                self.connection = self.connect()
            for i in data:
                self.connection.execute(query=i)
            return {"message": "DuckDB Operation successful"}
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail="Substrait DuckDB Internal Error while executing"
                "SQL Query: " + str(e),
            )

    def parse(self, data):
        try:
            if self.check()["db_health"] != "up and running":
                self.connection = self.connect()
            result = self.connection.get_substrait_json(data["query"]).fetchone()[0]
            return result
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail="Substrait DuckDB Internal Error while parsing SQL Query: "
                + str(e),
            )
