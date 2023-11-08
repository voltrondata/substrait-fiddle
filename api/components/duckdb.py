import os

import duckdb
from fastapi import HTTPException
from loguru import logger

# Pool size is default at 5 for maintaining 
# 5 concurrent DuckDB connection objects
POOL_SIZE = os.environ.get("DUCKDB_POOL_SIZE")



############################################################
# Class to manage DuckDB connections 
############################################################
class DuckDBConnection:
    def __init__(self):
        '''
            Constructor initializes the connection pool, 
            connects to the database, and creates the 
            default lineitem table. In the end, it
            calls the append_pool method which adds 
            connection objects in the pool.
        '''
        self.conn_pool = []

        create_lineitem_statement = """ 
                        CREATE TABLE IF NOT EXISTS lineitem(
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
        conn = duckdb.connect("../resources/duck.db")
        conn.execute(query = create_lineitem_statement)
        self.append_pool()


    def append_pool(self):
        for i in range(POOL_SIZE):
            conn = duckdb.connect("../resources/duck.db")
            conn.install_extension("substrait")
            conn.load_extension("substrait")
            self.conn_pool.append(conn)


    def check_pool(self):
        if len(self.conn_pool) == 0:
            self.append_pool()


    def get_connection(self):
        self.check_pool()
        con = self.conn_pool.pop(0)
        return con


############################################################
# Helper functions for DuckDB connections
############################################################

def check_duckdb_connection(con):
    '''
    Function checks if the database
    connection is healthy by executing 
    a query on the default table.
    '''
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


def execute_duckdb(query, con):
    '''
    Function executes a query on the DuckDB 
    instance.
    '''
    try:
        con.execute(query=query)
        return {"message": "DuckDB Operation successful"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Substrait DuckDB Internal Error while executing"
            "SQL Query: " + str(e),
        )


def delete_table_from_duckDB(table_name, con):
    '''
    Function drops table from DuckDB
    '''
    try:
        con.execute(query="DROP TABLE " + table_name + ";")
    except Exception as e:
        logger.error(e)


def parse_from_duckDB(query, con):
    '''
    Function translates a SQL query to a
    Substrait plan
    '''
    try:
        result = con.get_substrait_json(query).fetchone()[0]
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Substrait DuckDB Internal Error while parsing SQL Query: "
            + str(e),
        )
