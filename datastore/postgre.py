"""
This module defines the PostgreStorage class which handles PostgreSQL
storage operations, including table creation, data insertion, updates,
deletions, and selection queries.
"""

import logging
import psycopg2
from psycopg2 import sql
from datetime import datetime
from psycopg2 import pool # pylint: disable=unused-import
from datastore.db_config import DBConfig

# from loggers.loggers_config import LoggerConfig

# # logger_config = LoggerConfig('Postgre')

CREATE_CURRENCY_TABLE = """
    -- Table: public.currency
    CREATE TABLE IF NOT EXISTS public.currency (
        id SERIAL PRIMARY KEY,
        curr VARCHAR(10) NOT NULL UNIQUE
    );
    INSERT INTO public.currency (curr) VALUES
        ('AFN'), ('EUR'), ('ALL'), ('DZD'), ('USD'), ('AOA'), ('XCD'), ('ARS'), ('AMD'), ('AWG'), ('AUD'), 
        ('AZN'), ('BSD'), ('BHD'), ('BDT'), ('BBD'), ('BYN'), ('BZD'), ('XOF'), ('BMD'), ('INR'), ('BTN'), 
        ('BOB'), ('BOV'), ('BAM'), ('BWP'), ('NOK'), ('BRL'), ('BND'), ('BGN'), ('BIF'), ('CVE'), ('KHR'), 
        ('XAF'), ('CAD'), ('KYD'), ('CLP'), ('CLF'), ('CNY'), ('COP'), ('COU'), ('KMF'), ('CDF'), ('NZD'), 
        ('CRC'), ('HRK'), ('CUP'), ('CUC'), ('ANG'), ('CZK'), ('DKK'), ('DJF'), ('DOP'), ('EGP'), ('SVC'), 
        ('ERN'), ('SZL'), ('ETB'), ('FKP'), ('FJD'), ('XPF'), ('GMD'), ('GEL'), ('GHS'), ('GIP'), ('GTQ'), 
        ('GBP'), ('GNF'), ('GYD'), ('HTG'), ('HNL'), ('HKD'), ('HUF'), ('ISK'), ('IDR'), ('XDR'), ('IRR'), 
        ('IQD'), ('ILS'), ('JMD'), ('JPY'), ('JOD'), ('KZT'), ('KES'), ('KPW'), ('KRW'), ('KWD'), ('KGS'), 
        ('LAK'), ('LBP'), ('LSL'), ('ZAR'), ('LRD'), ('LYD'), ('CHF'), ('MOP'), ('MKD'), ('MGA'), ('MWK'), 
        ('MYR'), ('MVR'), ('MRU'), ('MUR'), ('XUA'), ('MXN'), ('MXV'), ('MDL'), ('MNT'), ('MAD'), ('MZN'), 
        ('MMK'), ('NAD'), ('NPR'), ('NIO'), ('NGN'), ('OMR'), ('PKR'), ('PAB'), ('PGK'), ('PYG'), ('PEN'), 
        ('PHP'), ('PLN'), ('QAR'), ('RON'), ('RUB'), ('RWF'), ('SHP'), ('WST'), ('STN'), ('SAR'), ('RSD'), 
        ('SCR'), ('SLL'), ('SGD'), ('XSU'), ('SBD'), ('SOS'), ('SSP'), ('LKR'), ('SDG'), ('SRD'), ('SEK'), 
        ('CHE'), ('CHW'), ('SYP'), ('TWD'), ('TJS'), ('TZS'), ('THB'), ('TOP'), ('TTD'), ('TND'), ('TRY'), 
        ('TMT'), ('UGX'), ('UAH'), ('AED'), ('USN'), ('UYU'), ('UYI'), ('UYW'), ('UZS'), ('VUV'), ('VES'), 
        ('VND'), ('YER'), ('ZMW'), ('ZWL'), ('XBA'), ('XBB'), ('XBC'), ('XBD'), ('XTS'), ('XXX'), ('XAU'), 
        ('XPD'), ('XPT'), ('XAG'), ('AFA'), ('FIM'), ('ALK'), ('ADP'), ('ESP'), ('FRF'), ('AOK'), ('AON'), 
        ('AOR'), ('ARA'), ('ARP'), ('ARY'), ('RUR'), ('ATS'), ('AYM'), ('AZM'), ('BYB'), ('BYR'), ('BEC'), 
        ('BEF'), ('BEL'), ('BOP'), ('BAD'), ('BRB'), ('BRC'), ('BRE'), ('BRN'), ('BRR'), ('BGJ'), ('BGK'), 
        ('BGL'), ('BUK'), ('HRD'), ('CYP'), ('CSJ'), ('CSK'), ('ECS'), ('ECV'), ('GQE'), ('EEK'), ('XEU'), 
        ('GEK'), ('DDM'), ('DEM'), ('GHC'), ('GHP'), ('GRD'), ('GNE'), ('GNS'), ('GWE'), ('GWP'), ('ITL'), 
        ('ISJ'), ('IEP'), ('ILP'), ('ILR'), ('LAJ'), ('LVL'), ('LVR'), ('LSM'), ('ZAL'), ('LTL'), ('LTT'), 
        ('LUC'), ('LUF'), ('LUL'), ('MGF'), ('MVQ'), ('MLF'), ('MTL'), ('MTP'), ('MRO'), ('MXP'), ('MZE'), 
        ('MZM'), ('NLG'), ('NIC'), ('PEH'), ('PEI'), ('PES'), ('PLZ'), ('PTE'), ('ROK'), ('ROL'), ('STD'), 
        ('CSD'), ('SKK'), ('SIT'), ('RHD'), ('ESA'), ('ESB'), ('SDD'), ('SDP'), ('SRG'), ('CHC'), ('TJR'), 
        ('TPE'), ('TRL'), ('TMM'), ('UGS'), ('UGW'), ('UAK'), ('SUR'), ('USS'), ('UYN'), ('UYP'), ('VEB'), 
        ('VEF'), ('VNC'), ('YDD'), ('YUD'), ('YUM'), ('YUN'), ('ZRN'), ('ZRZ'), ('ZMK'), ('ZWC'), ('ZWD'), 
        ('ZWN'), ('ZWR'), ('XFO'), ('XRE'), ('XFU')
    ON CONFLICT (curr) DO NOTHING;
"""

CREATE_TICKER_TABLE = """
    -- Table: public.ticker
    CREATE TABLE IF NOT EXISTS public.ticker (
        id SERIAL PRIMARY KEY,
        curr1 INTEGER REFERENCES public.currency(id) ON DELETE CASCADE,
        curr2 INTEGER REFERENCES public.currency(id) ON DELETE CASCADE,
        ticker VARCHAR(10) NOT NULL UNIQUE
    );
"""

CREATE_PRICE_TABLE = """
    -- Table: public.price
    CREATE TABLE IF NOT EXISTS public.price (
        id SERIAL PRIMARY KEY,
        ticker_code INTEGER NOT NULL UNIQUE REFERENCES public.ticker(id) ON DELETE CASCADE,
        datetime TIMESTAMPTZ,
        bid_size DOUBLE PRECISION,
        bid_price DOUBLE PRECISION,
        ask_size DOUBLE PRECISION,
        ask_price DOUBLE PRECISION,
        mid_price DOUBLE PRECISION
    );
"""

class PostgreStorage:
    """Class for handling PostgreSQL storage."""
    sid = "postgre"

    def __init__(self, db_config: DBConfig):
        self.default_db_params = {
            'dbname': 'postgres',  # Connect to the default 'postgres' database
            'user': db_config.db_user,
            'password': db_config.db_pass,
            'host': db_config.db_host,
            'port': db_config.db_port
        }
        
        self.db_params = {
            'dbname': db_config.db_name,
            'user': db_config.db_user,
            'password': db_config.db_pass,
            'host': db_config.db_host,
            'port': db_config.db_port
        }

        # Create database if it does not exist
        self.create_database_if_not_exists()

        # Create a connection pool to the database
        self.connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            **self.db_params
        )

        self.conn = self.get_connection()
        self.create_tables_if_not_exist(CREATE_CURRENCY_TABLE, "CURRENCY")
        self.create_tables_if_not_exist(CREATE_TICKER_TABLE, "TICKER")
        self.create_tables_if_not_exist(CREATE_PRICE_TABLE, "PRICE")

    def get_connection(self):
        """Get a connection from the connection pool."""
        return self.connection_pool.getconn()

    def commit(self):
        """Commit the current transaction."""
        self.conn.commit()

    def release_connection(self, connection):
        """Release a connection back to the connection pool."""
        self.connection_pool.putconn(connection)

    def create_database_if_not_exists(self):
        """Create the database if it does not exist."""
        connection = None
        try:
            # Connect to the default database
            connection = psycopg2.connect(**self.default_db_params)
            connection.autocommit = True  # Required to create a database
            with connection.cursor() as cursor:
                # Check if the database exists
                cursor.execute(sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), [self.db_params['dbname']])
                if cursor.fetchone():
                    logging.info("Database '%s' already exists.", self.db_params['dbname'])
                else:
                    # Create the database
                    cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.db_params['dbname'])))
                    logging.info("Database '%s' created.", self.db_params['dbname'])
        except psycopg2.Error as e:
            logging.error("Error creating database: %s", e)
        finally:
            if connection:
                connection.close()

    def create_tables_if_not_exist(self, create_table_queries, name):
        """Create tables in case they do not exist."""
        connection = self.get_connection()
        try:
            c = connection.cursor()
            with c as cursor:
                cursor.execute(create_table_queries)
            connection.commit()
            logging.info("%s tables created successfully (if they didn't exist).", name)
        except psycopg2.Error as e:
            logging.error("Error creating tables: %s", e)
        finally:
            if connection:
                self.release_connection(connection)

    def select_ticker(self):
        """Select and return ticker data."""
        connection = self.get_connection()
        c = connection.cursor()
        try:
            c.execute(
                """
                SELECT ct1.curr, ct2.curr, dt.ticker FROM ticker dt
                JOIN currency ct1 ON dt.curr1 = ct1.ID
                JOIN currency ct2 ON dt.curr2 = ct2.ID ORDER BY dt.ID;
                """
            )
            data = c.fetchall()
            return data

        except psycopg2.Error as e:
            logging.error("Error selecting ticker data: %s", e)
            return None
        finally:
            if connection:
                self.release_connection(connection)

    def select_currency(self):
        """Select and return currency data."""
        connection = self.get_connection()
        c = connection.cursor()
        try:
            c.execute(
                """
                SELECT * FROM currency;
                """
            )
            data = c.fetchall()
            return data

        except psycopg2.Error as e:
            logging.error("Error selecting currency data: %s", e)
            return None
        finally:
            if connection:
                self.release_connection(connection)

    def select_price(self):
        """Select and return price data."""
        connection = self.get_connection()
        c = connection.cursor()
        try:
            c.execute(
                """
                SELECT ct1.curr AS currency1_name, ct2.curr AS 
                    currency2_name, tk.ticker, pr.datetime, pr.bid_size, 
                    pr.bid_price, pr.ask_size, pr.ask_price, pr.mid_price 
                FROM price pr
                JOIN ticker tk ON pr.ticker_code = tk.ID
                JOIN currency ct1 ON tk.curr1 = ct1.ID
                JOIN currency ct2 ON tk.curr2 = ct2.ID ORDER BY pr.id;
                """
            )
            data = c.fetchall()
            return data
        except psycopg2.Error as e:
            logging.error("Error selecting price data: %s", e)
            return None
        finally:
            if connection:
                self.release_connection(connection)

    def insert_ticker(self, data):
        """Insert a new ticker."""
        connection = self.get_connection()
        try:
            c = connection.cursor()
            c.execute(
                """
                CREATE OR REPLACE FUNCTION 
                    insert_ticker(currency1_code VARCHAR, 
                                currency2_code VARCHAR, 
                                ticker_code VARCHAR) 
                RETURNS VOID AS $$
                BEGIN
                    INSERT INTO ticker (curr1, curr2, ticker)
                    VALUES ((SELECT ID FROM currency WHERE curr = currency1_code),
                            (SELECT ID FROM currency WHERE curr = currency2_code),
                            ticker_code);
                END;
                $$ LANGUAGE plpgsql;

                SELECT insert_ticker(%s, %s, %s);
                """,
                [data[0], data[1], data[2]]
            )
            connection.commit()
            logging.info("Ticker Inserted")
            self.insert_price(['Q', data[2], datetime.now(), 0.0, 0.0, 0.0, 0.0, 0.0])
        except psycopg2.Error as e:
            logging.error("Error inserting ticker: %s", e)
        finally:
            if connection:
                self.release_connection(connection)

    def update_ticker(self, data):
        """Update an existing ticker."""
        connection = self.get_connection()
        try:
            c = connection.cursor()
            c.execute(
                """
                UPDATE ticker
                SET curr1 = (SELECT ID FROM currency WHERE curr = %s),
                    curr2 = (SELECT ID FROM currency WHERE curr = %s),
                    ticker = %s
                WHERE ticker = %s;
                """,
                [data[0], data[1], data[2], data[3]]
            )
            connection.commit()
            logging.info("Ticker Updated")
        except psycopg2.Error as e:
            logging.error("Error updating ticker: %s", e)
        finally:
            if connection:
                self.release_connection(connection)

    def delete_ticker(self, data):
        """Delete a ticker and price data."""
        connection = self.get_connection()
        try:
            c = connection.cursor()
            c.execute(
                """
                BEGIN;

                DELETE FROM price WHERE ticker_code = (SELECT id FROM ticker WHERE ticker = %s);

                DELETE FROM ticker WHERE ticker = %s;
                
                COMMIT;
                """,
                [data, data]
            )
            connection.commit()
            logging.info("Ticker Deleted")
        except psycopg2.Error as e:
            logging.error("Error deleting ticker: %s", e)
        finally:
            if connection:
                self.release_connection(connection)

    def ticker_exists(self, currency1, currency2, ticker):
        """Check if a ticker exists in the database."""
        connection = self.get_connection()
        c = connection.cursor()
        try:
            c.execute(
                """
                SELECT 1 FROM ticker dt
                JOIN currency ct1 ON dt.curr1 = ct1.ID
                JOIN currency ct2 ON dt.curr2 = ct2.ID
                WHERE ct1.curr = %s AND ct2.curr = %s AND dt.ticker = %s;
                """,
                (currency1, currency2, ticker)
            )
            # Fetch one record, if it exists
            exists = c.fetchone() is not None
            return exists

        except psycopg2.Error as e:
            logging.error("Error checking if ticker exists: %s", e)
            return False
        finally:
            if connection:
                self.release_connection(connection)

    def insert_price(self, data):
        """Insert a new price data."""
        connection = self.get_connection()
        try:
            c = connection.cursor()
            c.execute(
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
                                                        
                    INSERT INTO price (ticker_code, datetime, bid_size, 
                                    bid_price, ask_size, ask_price, mid_price)
                    VALUES ((SELECT ID FROM ticker WHERE ticker = tickercode_node),
                            datetime_node, bid_size_node, bid_price_node, 
                            ask_size_node, ask_price_node, mid_price_node)
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
                [data[1], data[2], data[3], data[4], data[6], data[7]]
            )
            connection.commit()
            logging.info("Data Inserted")
        except psycopg2.Error as e:
            logging.error("Error inserting data: %s", e)
        finally:
            if connection:
                self.release_connection(connection)

        
