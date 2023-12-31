import json
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Iterable, List, Optional
import psycopg2
from psycopg2 import pool

CREATE_CURRENCY_TABLE="""
    -- Table: public.currency
    CREATE TABLE IF NOT EXISTS public.currency (
        id SERIAL PRIMARY KEY,
        curr VARCHAR(10) NOT NULL UNIQUE
    );
    INSERT INTO public.currency (curr) VALUES
        ('USD'),
        ('EUR'),
        ('JPY')
    ON CONFLICT (curr) DO NOTHING;
"""

CREATE_TICKER_TABLE="""
    -- Table: public.ticker
    CREATE TABLE IF NOT EXISTS public.ticker (
        id SERIAL PRIMARY KEY,
        curr1 INTEGER REFERENCES public.currency(id),
        curr2 INTEGER REFERENCES public.currency(id),
        ticker VARCHAR(10) NOT NULL UNIQUE
    );
"""

CREATE_PRICE_TABLE="""
    -- Table: public.price
    CREATE TABLE IF NOT EXISTS public.price (
        id SERIAL PRIMARY KEY,
        ticker_code INTEGER UNIQUE REFERENCES public.ticker(id),
        datetime TIMESTAMPTZ,
        bid_size DOUBLE PRECISION,
        bid_price DOUBLE PRECISION,
        ask_size DOUBLE PRECISION,
        ask_price DOUBLE PRECISION,
        mid_price DOUBLE PRECISION
    );
"""

class PostgreStorage():
    sid = "postgre"

    def __init__(self,dbname,user,password,host,port):
        db_params = {
            "dbname" : dbname,
            "user":user,
            "password":password,
            "host":host,
            "port":port,
        }
        
        self.connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            **db_params
        )

        self.conn = self.get_connection()
        self.create_tables_if_not_exist(CREATE_CURRENCY_TABLE)
        self.create_tables_if_not_exist(CREATE_TICKER_TABLE)
        self.create_tables_if_not_exist(CREATE_PRICE_TABLE)

    def get_connection(self):
        conn_ = self.connection_pool.getconn()
        return conn_
    
    def commit(self):
        self.conn.commit()
        # self.last_commit = datetime.now()
        # self.num_uncommitted_statements = 0

    def release_connection(self, connection):
        self.connection_pool.putconn(connection)

    def create_tables_if_not_exist(self,create_table_queries):
        connection = self.get_connection()
        try:
            c = connection.cursor()
            with c as cursor:
                cursor.execute(create_table_queries)
            connection.commit()
            print("Tables created successfully (if they didn't exist).")
        except psycopg2.Error as e:
            print("Error creating tables:", e)
        finally:
            if connection:
                self.release_connection(connection)

    def select_ticker(self):
        connection = self.get_connection()
        c = connection.cursor()
        try:
            res = c.execute(
                """
                SELECT ct1.curr, ct2.curr, dt.ticker FROM ticker dt
                JOIN currency ct1 ON dt.curr1 = ct1.ID
                JOIN currency ct2 ON dt.curr2 = ct2.ID ORDER BY dt.ID;
                """)
            data = c.fetchall()
            return data
        except Exception as e:
                print(f"Error fetching data: {e}")
        finally:
            if connection:
                self.release_connection(connection)


    def select_currency(self):
        connection = self.get_connection()
        c = connection.cursor()
        try:
            res = c.execute(
                """
                SELECT * FROM currency;
                """
            )
            data = c.fetchall()
            return data
            
        except Exception as e:
            print(f"Error select price tabel : {e}")
        finally:
            if connection:
                self.release_connection(connection)            

    def select_price(self):
        connection = self.get_connection()
        c = connection.cursor()
        try:
            res = c.execute(
                """
                SELECT ct1.curr AS currency1_name, ct2.curr AS currency2_name, tk.ticker, pr.datetime, pr.bid_size, pr.bid_price, pr.ask_size, pr.ask_price, pr.mid_price FROM price pr
                JOIN ticker tk ON pr.ticker_code = tk.ID
                JOIN currency ct1 ON tk.curr1 = ct1.ID
                JOIN currency ct2 ON tk.curr2 = ct2.ID ORDER BY pr.id;
                """
            )
            data = c.fetchall()
            return data
            
        except Exception as e:
            print(f"Error select price tabel : {e}")
        finally:
            if connection:
                self.release_connection(connection)

    def insert_ticker(self, data):
        connection = self.get_connection()
        try:
            c = connection.cursor()
            res = c.execute(
                """
                CREATE OR REPLACE FUNCTION insert_ticker(currency1_code VARCHAR, currency2_code VARCHAR, ticker_code VARCHAR) RETURNS VOID AS $$
                BEGIN
                    INSERT INTO ticker (curr1, curr2, ticker)
                    VALUES ((SELECT ID FROM currency WHERE curr = currency1_code),
                            (SELECT ID FROM currency WHERE curr = currency2_code),
                            ticker_code);
                END;
                $$ LANGUAGE plpgsql;

                SELECT insert_ticker(%s, %s, %s);
                """,
                [data[0],data[1],data[2]]
            )
            connection.commit()
            print("Ticker Inserted")
        except Exception as e:
            print(f"Error inserting ticker: {e}")
        finally:
            if connection:
                self.release_connection(connection)

    def update_ticker(self,data):
        connection = self.get_connection()
        try:
            c = connection.cursor()
            res = c.execute(
                """
                UPDATE ticker
                SET curr1 = (SELECT ID FROM currency WHERE curr = %s),
                    curr2 = (SELECT ID FROM currency WHERE curr = %s),
                    ticker = %s
                WHERE ticker = %s;
                """,
                [data[0],data[1],data[2],data[3]]
            )
            connection.commit()
            print("Ticker Updated")
        except Exception as e:
            print(f"Error updating ticker: {e}")
        finally:
            if connection:
                self.release_connection(connection)


    def delete_ticker(self,data):
        connection = self.get_connection()
        try:
            c = connection.cursor()
            res = c.execute(
                """
                DELETE FROM ticker WHERE ticker = %s;
                """,
                [data]
            )
            connection.commit()
            print(data)
            print("Ticker Deleted")
        except Exception as e:
            print(f"Error deleting ticker: {e}")
        finally:
            if connection:
                self.release_connection(connection)
    
    def insert_price(self, data):
        connection = self.get_connection()
        # print(data)
        try:
            c = connection.cursor()
            res = c.execute(
                """
                CREATE OR REPLACE FUNCTION insert_price(tickercode_node VARCHAR, 
										datetime_node TIMESTAMPTZ, 
										bid_size_node FLOAT, 
										bid_price_node FLOAT, 
										ask_size_node FLOAT,
									   	ask_price_node FLOAT) 
										RETURNS VOID AS $$
                DECLARE
                    mid_price_node FLOAT;
                BEGIN
                    mid_price_node := (bid_price_node + ask_price_node) / 2.0;									
                                                        
                    INSERT INTO price (ticker_code, datetime, bid_size, bid_price, ask_size, ask_price, mid_price)
                    VALUES ((SELECT ID FROM ticker WHERE ticker = tickercode_node),
                            datetime_node, bid_size_node, bid_price_node, ask_size_node, ask_price_node,
                            mid_price_node)
                    ON CONFLICT (ticker_code) DO UPDATE
                    SET datetime = EXCLUDED.datetime,
                        bid_size = EXCLUDED.bid_size,
                        bid_price = EXCLUDED.bid_price,
                        ask_size = EXCLUDED.ask_size,
                        ask_price = EXCLUDED.ask_price,
                        mid_price = EXCLUDED.mid_price;
                END;
                $$ LANGUAGE plpgsql;

                SELECT insert_price(%s, %s, %s, %s, %s, %s);
                """,
                [data[1],data[2],data[3],data[4],data[6],data[7]]
            )
            connection.commit()
            print("Data Inserted")
        except Exception as e:
            print(f"Error inserting data: {e}")
        finally:
            if connection:
                self.release_connection(connection)

