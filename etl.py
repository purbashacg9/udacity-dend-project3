import configparser
import psycopg2
from sql_queries import copy_table_queries, insert_table_queries


def load_staging_tables(cur, conn):
    """
    Description: Populate staging tables in Redshift database from data files in S3. copy_table_queries is a list of COPY queries to load data from S3 into staging_songs and staging_events tables.
    :param cur: psycopg2 cursor object - Database cursor
    :param conn: psycopg2 connection object encapsulating the Database session.
    """
    for query in copy_table_queries:
        cur.execute(query)
        conn.commit()


def insert_tables(cur, conn):
    """
    Description: Populate Songplay analysis tables in Redshift database from staging tables. insert_table_queries is a list of INSERT queries for the tables - songplays, songs, artists, user and time.
    :param cur: psycopg2 cursor object - Database cursor
    :param conn: psycopg2 connection object encapsulating the Database session
    """
    for query in insert_table_queries:
        cur.execute(query)
        conn.commit()


def main():
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()

    load_staging_tables(cur, conn)
    insert_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()
